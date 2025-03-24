import torch
import keyboard
from pytorch_game import create_game as Environment
from pytorch_game import Agent, ReplayMemory, Experience, Qvalues, extract_tensors
from dqn import DQN
import wandb
from tictoc import tictoc as tt


def train():
    project = 'CartPole'
    name = 'target'
    file_load = 'meta/last_train.pth'
    file_training = 'meta/last_train.pth'

    DEVICE = 'cpu'        # 'cuda'
    LOAD_WEIGHTS = True
    RENDER = False
    LOG = True
    VERBOSE_EVERY_N_EPISODES = 10
    SAVE_EVERY_N_EPISODES = 1000

    em = Environment(render=RENDER)
    n_actions = em.actions_size
    n_states = em.states_size

    # hiperparameters
    dims = [n_states, 128, 128, n_actions]
    batch_size = 512*8
    gamma = 0.99
    eps_decay = 0.00000005
    target_update = 200  # episodios
    learning_rate = 0.001   # 0.00005
    memory_size = 100000
    steps_train = 512

    eps_start = 1.0
    eps_end = 0.15
    num_episodes = 1000000

    steps_since_train = 0
    best_score = -1000000000

    device = torch.device(DEVICE if torch.cuda.is_available() else 'cpu')
    print(f'{device=}')

    if LOAD_WEIGHTS:
        eps_start = 0.5

    agent = Agent(eps_start, eps_end, eps_decay, n_actions, device)
    memory = ReplayMemory(memory_size)

    target_net = DQN(dims, device)
    police_net = DQN(dims, device)

    if LOAD_WEIGHTS:
        police_net.load_state_dict(torch.load(file_load, weights_only=False))

    target_net.load_state_dict(police_net.state_dict())
    target_net.eval()
    # optimizer = torch.optim.RMSprop(police_net.parameters())
    optimizer = torch.optim.Adam(params=police_net.parameters(), lr=learning_rate)



    if LOG:
        wandb.login(key='b00b29296f083fe05f4960f8822f67599808a3c8')
        # wandb.require("legacy-service")
        wandb.init(project=project, name=name)
        wandb.config.file = file_training
        wandb.config.dims = dims
        wandb.config.batch_size = batch_size
        wandb.config.gamma = gamma
        wandb.config.eps_decay = eps_decay
        wandb.config.target_update = target_update
        wandb.config.learning_rate = learning_rate
        wandb.config.memory_size = memory_size
        wandb.config.steps_train = steps_train
        wandb.watch(police_net)

    for episode in range(num_episodes):
        tt.tic()
        state = em.reset_system()
        score = 0
        sim_steps = 0
        train_steps = 0
        done = False
        while not done:
            # if keyboard.is_pressed('+'):
            #     em.enable_rendering(True)
            # if keyboard.is_pressed('-'):
            #     em.enable_rendering(False)

            action = agent.select_action(state, police_net)
            next_state, reward, done = em.simulate_system(action.item())
            sim_steps += 1

            memory.push(Experience(state.to(device), action.to(device), next_state.to(device), reward.to(device)))
            state = next_state
            score += reward.item()
            steps_since_train += 1

            if (steps_since_train >= steps_train) and memory.can_provide_sample(batch_size):
                steps_since_train = 0
                experiences = memory.sample(batch_size)
                states, actions, rewards, next_states = extract_tensors(experiences)

                current_q_values = Qvalues.get_current(police_net, states.to(device), actions)
                next_q_values = Qvalues.get_next(target_net, next_states.to(device), device)
                target_q_values = ((next_q_values * gamma) + rewards)

                loss = torch.nn.functional.mse_loss(current_q_values, target_q_values.unsqueeze(1)).to(device)
                # loss = torch.nn.functional.smooth_l1_loss(current_q_values, target_q_values.unsqueeze(1))
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                train_steps += 1

        tt.toc()

        if LOG:
            wandb.log({"score": score,
                       "eps": agent.current_rate,
                       "episode_time": tt.elapsed,
                       "sim_steps": sim_steps,
                       "train_steps": train_steps})

        if best_score < score:
            best_score = score
            name, ext = file_training.rsplit(".", 1)
            torch.save(police_net.state_dict(), f'{name}_best_score.{ext}')

        if episode % VERBOSE_EVERY_N_EPISODES == 0:
            print(f'{episode=}, {sim_steps=}, {train_steps=}, {score=} | {best_score=}, elapsed={tt:.6f}')

        if episode % SAVE_EVERY_N_EPISODES == 0:
            torch.save(police_net.state_dict(), file_training)

        if episode % target_update == 0:
            target_net.load_state_dict(police_net.state_dict())


if __name__ == '__main__':
    train()