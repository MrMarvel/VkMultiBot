from module_controller import ModuleController
from src.modules.test_module.test_module import MyModule

if __name__ == '__main__':
    module_controller = ModuleController()
    module_controller.start_module(MyModule())
    module_controller.start_module(MyModule())
    module_controller.start_module(MyModule())
    module_controller.start_module(MyModule())
    module_controller.start_module(MyModule())
    module_controller.destroy_modules()
