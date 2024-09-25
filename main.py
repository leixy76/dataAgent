import loguru

from dataset_text_sft import test_text_sft_dataset
from image_qa_generator import execute_image_qa_generator
from dotenv import load_dotenv
load_dotenv()
if __name__ == "__main__":
    loguru.logger.info("dataAgent starting...")
    execute_image_qa_generator()