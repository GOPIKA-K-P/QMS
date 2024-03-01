from aws_lambda_powertools.logging.logger import Logger
# from aws_lambda_powertools.metrics.metrics import Metrics
# from aws_lambda_powertools.tracing.tracer import Tracer

METRICS_NAMESPACE = 'FAI_DETAILS'
SERVICE_NAME = "FAI_DETAILS"

logger: Logger = Logger(service=SERVICE_NAME)
# tracer: Tracer = Tracer()
# metrics = Metrics(namespace=METRICS_NAMESPACE)
