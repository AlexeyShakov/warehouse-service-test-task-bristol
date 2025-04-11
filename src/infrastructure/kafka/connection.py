from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Optional
from src.infrastructure import logger
from src.config import get_project_settings


SETTINGS = get_project_settings()

KAFKA_BOOTSTRAP_SERVERS = f"{SETTINGS.kafka_host}:9092"
KAFKA_TOPIC = SETTINGS.kafka_topic

PRODUCER: Optional[AIOKafkaProducer] = None
CONSUMER: Optional[AIOKafkaConsumer] = None


async def init_kafka_producer():
    global PRODUCER
    PRODUCER = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await PRODUCER.start()
    logger.LOGGER.info("Kafka producer started")


async def init_kafka_consumer():
    global CONSUMER
    CONSUMER = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    await CONSUMER.start()
    logger.LOGGER.info("Kafka consumer started")


async def stop_kafka():
    global PRODUCER, CONSUMER
    if PRODUCER:
        await PRODUCER.stop()
        logger.LOGGER.info("Kafka producer stopped")
    if CONSUMER:
        await CONSUMER.stop()
        logger.LOGGER.info("Kafka consumer stopped")
