from module_controller import ModuleController
from src.modules.informator_module.main import InformatorModule
from src.modules.queue_module.src.queue_vk_bot_mrmarvel.app import QueueModule

if __name__ == '__main__':
    module_controller = ModuleController()
    module_controller.start_module(QueueModule())
    module_controller.start_module(InformatorModule())
    module_controller.join()
    module_controller.destroy_modules()
