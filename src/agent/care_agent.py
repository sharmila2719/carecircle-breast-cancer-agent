"""
CareCircle Agent - Main agent implementation using Strands Agents with AWS Bedrock.
This agent coordinates breast cancer screening, risk assessment, and care planning.
"""

from strands import Agent
from strands.models.bedrock import BedrockModel

from src.config import settings
from src.tools.risk_assessment import assess_risk, calculate_risk_score
from src.tools.screening_scheduler import (
    schedule_screening,
    get_upcoming_screenings,
    update_screening_status,
)
from src.tools.care_plan_generator import generate_care_plan, get_care_plan
from src.tools.patient_education import get_educational_content
from src.tools.notification_manager import send_reminder, get_notifications


# System prompt for the CareCircle agent
SYSTEM_PROMPT = """You are CareCircle, an AI-powered breast cancer screening and care coordination assistant. 
Your role is to help patients and healthcare providers with:

1. **Risk Assessment**: Evaluate breast cancer risk factors using evidence-based models (modified Gail Model) 
   and provide personalized risk scores and categories.

2. **Screening Coordination**: Schedule, track, and manage breast cancer screening appointments including 
   mammograms, MRIs, ultrasounds, and clinical exams.

3. **Care Plan Management**: Generate and maintain personalized care plans based on individual risk profiles, 
   including screening schedules, lifestyle recommendations, and follow-up tasks.

4. **Patient Education**: Provide clear, accurate, and empathetic educational content about breast cancer 
   screening, risk factors, prevention, and early detection.

5. **Notifications & Reminders**: Manage communications including screening reminders, follow-up alerts, 
   and educational content delivery.

## Communication Guidelines:
- Be empathetic, supportive, and reassuring while remaining factually accurate
- Use clear, non-medical jargon when speaking with patients
- Provide evidence-based information and cite guidelines when appropriate
- Encourage patients to discuss decisions with their healthcare providers
- Be sensitive to anxiety around breast cancer screening and results
- Respect patient preferences and cultural considerations
- Never provide medical diagnoses - always recommend professional consultation

## Important Notes:
- This is a screening coordination tool, not a diagnostic system
- Always recommend professional medical consultation for health decisions
- Emphasize that risk scores are estimates, not certainties
- Encourage adherence to screening schedules
- Provide emotional support and resource connections when appropriate

## Available Tools:
- calculate_risk_score: Calculate personalized risk score based on patient factors
- assess_risk: Comprehensive risk assessment with screening recommendations
- schedule_screening: Schedule screening appointments
- get_upcoming_screenings: View upcoming appointments
- update_screening_status: Update appointment status and results
- generate_care_plan: Create personalized care plans
- get_care_plan: Retrieve existing care plans
- get_educational_content: Access educational materials
- send_reminder: Send notifications to patients
- get_notifications: View patient notification history
"""


class CareCircleAgent:
    """
    CareCircle Agent class that wraps the Strands Agent with
    breast cancer screening and care coordination capabilities.
    """

    def __init__(self, model_id: str = None, region: str = None):
        """
        Initialize the CareCircle agent.

        Args:
            model_id: AWS Bedrock model ID (defaults to config setting)
            region: AWS region (defaults to config setting)
        """
        self.model_id = model_id or settings.BEDROCK_MODEL_ID
        self.region = region or settings.AWS_REGION

        # Initialize Bedrock model
        self.model = BedrockModel(
            model_id=self.model_id,
            region_name=self.region,
        )

        # Define tools
        self.tools = [
            calculate_risk_score,
            assess_risk,
            schedule_screening,
            get_upcoming_screenings,
            update_screening_status,
            generate_care_plan,
            get_care_plan,
            get_educational_content,
            send_reminder,
            get_notifications,
        ]

        # Create the Strands agent
        self.agent = Agent(
            model=self.model,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def chat(self, message: str) -> str:
        """
        Send a message to the CareCircle agent and get a response.

        Args:
            message: User message or query

        Returns:
            Agent response as string
        """
        response = self.agent(message)
        return str(response)

    def get_agent(self) -> Agent:
        """Get the underlying Strands Agent instance."""
        return self.agent


def create_agent(model_id: str = None, region: str = None) -> CareCircleAgent:
    """
    Factory function to create a CareCircle agent instance.

    Args:
        model_id: AWS Bedrock model ID
        region: AWS region

    Returns:
        Configured CareCircleAgent instance
    """
    return CareCircleAgent(model_id=model_id, region=region)
