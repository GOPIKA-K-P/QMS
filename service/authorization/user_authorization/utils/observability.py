from aws_lambda_powertools.logging.logger import Logger
# from aws_lambda_powertools.metrics.metrics import Metrics
# from aws_lambda_powertools.tracing.tracer import Tracer

METRICS_NAMESPACE = 'CURRENT_SHIFT_INFO_V1'
SERVICE_NAME = "CURRENT_SHIFT_INFO_V1"

logger: Logger = Logger(service=SERVICE_NAME)
# tracer: Tracer = Tracer()
# metrics = Metrics(namespace=METRICS_NAMESPACE)
