## What is this directory?
app.py is the flask webserver that acts as the backend entrypoint of the lollms-webui. 

## Why this directory?
app.py is/was a huge monofile with 2300+ lines of code at the root of the project. It worked fine, but is much more difficult to read through and manage than one split into multiple files.

## How was it done?
We use a concept called 'Monkey Patching' to do something like this:
```python
main.py
class Foo():
    from world import bar, car

world.py
def bar(self):
    pass
def car(self):
    pass
```

This lets us define methods in a separate file from the class itself. It's nonstandard practice to organize your code this way, but it gives an improvement over the previous organization my making the code organization adhere to a directory/tree structure. This should have 0 effect on the code, only on developer organization.

## Directories
The two top-level directories inside LoLLMsWebUI_server are `config` and `methods`. Config is meant to be helper scripts and configuration. Methods is where all the class methods with (self) as a param were rehomed. There are generally 6 high-level categories for these functions, but their only function is to organize the code. As such, changing directory names, file names, and which method goes in which file is expected over time.

## What could be better?
Directories were named and chosen loosely based on methods' apparent functionality. It expected that over time these will get shuffled around as maintiners figure out what works best.
Bot related to this refactor, there are serveral static methods throughout the code. These use (self) as a parameter, but should just be an independent function or use the `@staticmethod` decorator.
Also, several functions access shared mutable state without explicitly accepting parameters to modify. It would be better to not do that. Generally, more functional (i.e. using functions) code tends to be easier to maintain and reason about, easier to bugfix, and easier to add features to.