import loguru

from image_qa_generator import  execute_image_qa_generator

if __name__ == "__main__":
    loguru.logger.info("dataAgent starting...")
    execute_image_qa_generator()