from module_controller import ModuleController
from src.modules.queue_module.VkBot.src.queue_vk_bot_mrmarvel.app import QueueModule
from src.modules.test_module.test_module import MyModule

if __name__ == '__main__':
    module_controller = ModuleController()
    module_controller.start_module(QueueModule())
