
resource "aws_lambda_function" "telegrampocketbot" {
  depends_on = [ aws_cloudwatch_event_rule.morning-daily, aws_apigatewayv2_api.telegram-webhook ]
  filename         = "../release/telegram-pocket-bot.zip"
  source_code_hash = filebase64sha256("../release/telegram-pocket-bot.zip")

  function_name = "telegram-pocket-bot2"
  description   = ""
  memory_size   = 128
  timeout       = 30
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  architectures = ["arm64"]
  ephemeral_storage {
    size = 512
  }
  environment {
    variables = {
      CHAT_ID                       = var.telegram_chat_id
      POCKET_ACCESS_TOKEN           = var.pocket_access_token
      POCKET_CONSUMER_ID            = var.pocket_consumer_id
      TELEGRAM_WEBHOOK_SECRET_TOKEN = var.telegram_webhook_secret
      BOT_TOKEN                     = var.bot_token
      WEATHER_LOCATION              = var.weather_location
    }
  }

  layers = [
    data.klayers_package_latest_version.requests.arn,
    aws_lambda_layer_version.pocket-api.arn,
    aws_lambda_layer_version.python-weather.arn
  ]

  role = aws_iam_role.lambda_exec.arn
}

data "klayers_package_latest_version" "requests" {
  region = "us-east-1"
  name   = "requests"
}

resource "aws_lambda_layer_version" "pocket-api" {
  filename         = "layers/pocket-api.zip"
  source_code_hash = filebase64sha256("layers/pocket-api.zip")
  layer_name       = "pocket-api"
}

resource "aws_lambda_layer_version" "python-weather" {
  filename         = "layers/python-weather.zip"
  source_code_hash = filebase64sha256("layers/python-weather.zip")
  layer_name       = "python-weather"
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  inline_policy {
    name = "lambda_logging"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Resource = "arn:aws:logs:us-east-1:170788249081:*"
        },
        {
          Effect = "Allow"
          Action = [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Resource = "arn:aws:logs:us-east-1:170788249081:log-group:/aws/lambda/telegram-pocket-bot:*"
        }
      ]
    })
  }
}

resource "aws_lambda_function_event_invoke_config" "runtime_management_config" {
  function_name = aws_lambda_function.telegrampocketbot.arn
  #update_runtime_on              = "Auto"
}