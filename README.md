<h1 align="center">🥈 Team Second Place's Smart Home System — Microcontroller Application</h1>

## Prerequisites

1. Python **3.10.9 version exactly** (3.11 is too new and 3.9 is too old)

   - Use [pyenv-win](https://github.com/pyenv-win/pyenv-win) if working on the project on your own Windows computer:
     - Install it with the **PowerShell** terminal command
       ```ps
       Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
       ```
   - Use pyenv if working on the project on a Raspberry Pi (or other Linux machine):
     - Install its prerequisites with the terminal commands
       ```bash
       sudo apt update
       sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
       ```
     - Install it with the terminal command
       ```bash
       curl https://pyenv.run | bash
       ```
   - Then, for either case, **close the terminal entirely and open it again** install Python 3.10.9 with the terminal command
     ```bash
     pyenv install 3.10.9
     ```
   - **If the setup process above isn't working out**, try using [the official installer](https://www.python.org/downloads/release/python-3109/) if working on the project on your own Windows computer

2. Poetry

- Install it with the terminal command if working on the project on your own Windows computer

  ```sh
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
  ```

- Install it with the terminal command if working on the project on the Raspberry Pi (or other Linux machine)
  ```sh
  curl -sSL https://install.python-poetry.org | python3 -
  ```

3. Git

   - Use the [official installer for Windows](https://git-scm.com/download/win) if working on the project on your own computer
   - Use `sudo apt install git` when on the Raspberry Pi

4. A code editor, [like VS Code](https://code.visualstudio.com/) (not the same thing as Visual Studio), so you can work on the project and see errors and get automatic suggestions. Ask for help setting the editor to use the virtual environment that Poetry creates for the project.

## Download the application

1. Run the terminal command `git clone https://github.com/team-second-place/microcontroller-application` in the directory where you want to save the project

2. Enter the `microcontroller-application` directory it created

3. Run the terminal commands

   ```sh
   poetry lock
   poetry install --with test
   ```

   to install the project's runtime dependencies, its development dependencies, and its testing dependencies.

   (Though it probably won't ever matter to know, if you were to run `poetry install --without dev,test`, then only the runtime dependencies would be installed, like we would do if we wanted to make a production version of the system as optimal as possible).

## Develop the application

### Automated testing

Use `poetry run pytest` to run the unit tests and integration tests.

The first time you download the application without making any changes and run this, all the tests should pass. That is, unless we've deliberately written failing tests 😅.

### Run the whole application

Use `poetry run python -m microcontroller_application` to run the application.

Depending on how far into project development we are, this might fail _on your own computer_ because it's trying to access GPIO that doesn't exist for example.

## Sharing code updates you've made

Ask for help committing and pushing code to this GitHub repository.

## Upload the application to a Raspberry Pi

See the above steps but perform them on the Raspberry Pi instead.

More information about how to make sure that the Raspberry Pi is always running the application and restarting it if it ever crashes will be included here once we learn how to do that.
