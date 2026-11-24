# BB84-Sim

## Quickstart
1. You must have python installed. I have 3.8.2, but I imagine later versions will run fine.
2. Open a terminal in the base directory and run the following command:
```
python -m venv .venv
```
3. When it is done making the virtual environment you should now have a folder called .venv in your workspace. Run this command to activate it, you will need to make sure it is active in the terminal whenever you want to run the program.
```
\.venv\Scripts\activate
```
4. When it is done make sure the terminal prompt has a (.venv) at the start of the line.
5. Run:
```
pip install -r REQUIREMENTS.txt
```
6. That should have all of the prerequisites and now you are safe to run the program with:
```
python \src\sim.py [args...]
```
7. Make sure to replace '[args...]' with the arguments you want to use. If you don't know what those are then type:
```
python \src\simp.py -h
```
8. The step above will give you a list of arguments. Enjoy!