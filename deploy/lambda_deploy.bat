@echo off
REM CareCircle - AWS Lambda Serverless Deployment Script (Windows)
REM Prerequisites: AWS SAM CLI installed, AWS credentials configured

echo.
echo ====================================================
echo   CareCircle - Serverless Lambda Deployment
echo ====================================================
echo.

REM Check SAM CLI
where sam >nul 2>&1
if errorlevel 1 (
    echo ERROR: AWS SAM CLI not found.
    echo Install: pip install aws-sam-cli
    echo Or visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
    pause
    exit /b 1
)

REM Check AWS CLI
where aws >nul 2>&1
if errorlevel 1 (
    echo ERROR: AWS CLI not found.
    echo Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    pause
    exit /b 1
)

echo [1/2] Building Lambda package...
sam build
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [2/2] Deploying to AWS Lambda...
sam deploy --guided

echo.
echo ====================================================
echo   Deployment complete!
echo ====================================================
echo.
echo Your API is live at the URL shown above.
echo Try: GET /docs for interactive API documentation
echo.
pause
