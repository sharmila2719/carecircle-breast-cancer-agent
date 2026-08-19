"""
Patient Education Tool for CareCircle.
Provides evidence-based educational content about breast cancer screening and prevention.
"""

from typing import Any

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def get_educational_content(topic: str, detail_level: str = "standard") -> dict[str, Any]:
    """
    Retrieve educational content about breast cancer screening and prevention.

    Args:
        topic: Education topic. Options:
            - breast_self_exam: How to perform breast self-examination
            - mammogram_overview: What to expect during a mammogram
            - risk_factors: Understanding breast cancer risk factors
            - screening_guidelines: Current screening guidelines by age/risk
            - genetic_testing: Understanding genetic testing for breast cancer
            - dense_breasts: Information about breast density
            - lifestyle_prevention: Lifestyle factors for prevention
            - early_detection: Importance of early detection
            - support_resources: Available support resources
            - myths_facts: Common myths vs facts about breast cancer
        detail_level: Level of detail (brief, standard, comprehensive)

    Returns:
        Educational content with key points, details, and resources
    """
    content_library = _get_content_library()

    topic_key = topic.lower().replace(" ", "_").replace("-", "_")

    if topic_key not in content_library:
        # Try fuzzy matching
        matching_topics = [k for k in content_library.keys() if topic_key in k or k in topic_key]
        if matching_topics:
            topic_key = matching_topics[0]
        else:
            return {
                "success": False,
                "error": f"Topic '{topic}' not found.",
                "available_topics": list(content_library.keys()),
                "suggestion": "Try one of the available topics listed above.",
            }

    content = content_library[topic_key]

    # Adjust based on detail level
    if detail_level == "brief":
        return {
            "success": True,
            "topic": content["title"],
            "summary": content["summary"],
            "key_points": content["key_points"][:3],
        }
    elif detail_level == "comprehensive":
        return {
            "success": True,
            "topic": content["title"],
            "summary": content["summary"],
            "key_points": content["key_points"],
            "detailed_content": content.get("detailed_content", ""),
            "faqs": content.get("faqs", []),
            "resources": content.get("resources", []),
            "references": content.get("references", []),
        }
    else:  # standard
        return {
            "success": True,
            "topic": content["title"],
            "summary": content["summary"],
            "key_points": content["key_points"],
            "resources": content.get("resources", []),
        }


def _get_content_library() -> dict:
    """Get the educational content library."""
    return {
        "breast_self_exam": {
            "title": "Breast Self-Examination Guide",
            "summary": "A breast self-exam (BSE) is a step-by-step method to check your breasts for changes. While not a replacement for clinical screenings, BSE helps you become familiar with your breasts so you can notice changes early.",
            "key_points": [
                "Perform BSE once a month, preferably 7-10 days after your period starts",
                "Use three levels of pressure: light (skin surface), medium (mid-tissue), and firm (deep tissue near ribs)",
                "Check in front of a mirror for visual changes and lying down for manual exam",
                "Look for lumps, skin dimpling, nipple changes, swelling, or discharge",
                "Report any changes to your healthcare provider promptly",
                "BSE is most effective when combined with regular clinical screenings",
            ],
            "detailed_content": """
Step-by-Step Breast Self-Exam:

1. VISUAL INSPECTION (Standing before a mirror):
   - Stand with arms at sides, then raise arms overhead
   - Look for changes in shape, size, skin texture, or nipple position
   - Check for dimpling, puckering, or redness

2. MANUAL EXAM (Lying down):
   - Place a pillow under your right shoulder, right arm behind head
   - Use left hand pads of 3 middle fingers to examine right breast
   - Use overlapping dime-sized circular motions
   - Cover entire breast from collarbone to bra line, armpit to cleavage
   - Repeat on other side

3. SHOWER CHECK:
   - Soapy skin makes it easier to feel changes
   - Use same circular motion technique
   - Check underarm area as well
            """,
            "faqs": [
                {
                    "q": "How often should I do a BSE?",
                    "a": "Once a month, ideally at the same time each month.",
                },
                {
                    "q": "What if I find a lump?",
                    "a": "Don't panic. Most lumps are benign. Contact your healthcare provider for evaluation.",
                },
                {
                    "q": "At what age should I start BSE?",
                    "a": "Starting in your 20s helps establish a baseline of what's normal for you.",
                },
            ],
            "resources": [
                {"name": "Video Tutorial: BSE Technique", "type": "video"},
                {"name": "Printable BSE Reminder Card", "type": "download"},
            ],
            "references": [
                "American Cancer Society Breast Self-Exam Guidelines",
                "National Breast Cancer Foundation BSE Resources",
            ],
        },
        "mammogram_overview": {
            "title": "Understanding Mammograms",
            "summary": "A mammogram is an X-ray of the breast used to detect breast cancer early, often before symptoms appear. Regular mammograms are the most effective screening tool for detecting breast cancer in its earliest stages.",
            "key_points": [
                "Mammograms can detect cancer up to 2 years before a lump can be felt",
                "The procedure takes about 15-30 minutes",
                "Some discomfort from breast compression is normal but brief",
                "3D mammography (tomosynthesis) provides more detailed images",
                "Annual mammograms are recommended starting at age 40 for average risk",
                "BI-RADS scoring system (0-6) is used to classify findings",
            ],
            "detailed_content": """
Types of Mammograms:
- Screening Mammogram: Routine check for those without symptoms
- Diagnostic Mammogram: More detailed exam when an issue is found
- 3D Mammogram (Tomosynthesis): Multiple angles for clearer images

BI-RADS Categories:
- 0: Incomplete - needs additional imaging
- 1: Negative - no findings
- 2: Benign - non-cancerous findings
- 3: Probably Benign - short-interval follow-up recommended
- 4: Suspicious - biopsy should be considered
- 5: Highly Suggestive of Malignancy - biopsy recommended
- 6: Known Malignancy - confirmed cancer
            """,
            "resources": [
                {"name": "What to Expect: Mammogram Day", "type": "guide"},
                {"name": "Understanding Your Mammogram Results", "type": "guide"},
            ],
            "references": [
                "American College of Radiology Mammography Guidelines",
                "USPSTF Screening Recommendations",
            ],
        },
        "risk_factors": {
            "title": "Understanding Breast Cancer Risk Factors",
            "summary": "Breast cancer risk is influenced by a combination of factors you can't change (like age and genetics) and factors you can modify (like lifestyle choices). Understanding your risk helps guide appropriate screening decisions.",
            "key_points": [
                "Being female and increasing age are the two biggest risk factors",
                "Only 5-10% of breast cancers are hereditary (BRCA1/BRCA2 mutations)",
                "Having risk factors doesn't mean you will develop breast cancer",
                "Dense breast tissue increases risk AND makes cancer harder to detect",
                "Modifiable factors include weight, exercise, alcohol, and smoking",
                "A combination of factors determines your overall risk level",
                "Regular screening is important regardless of risk level",
            ],
            "resources": [
                {"name": "Risk Assessment Calculator", "type": "tool"},
                {"name": "Family History Worksheet", "type": "download"},
            ],
            "references": [
                "National Cancer Institute Risk Factor Data",
                "Gail Model Risk Assessment",
            ],
        },
        "screening_guidelines": {
            "title": "Breast Cancer Screening Guidelines",
            "summary": "Screening guidelines vary by age and risk level. Multiple organizations provide recommendations, and your healthcare provider can help determine the best plan for you.",
            "key_points": [
                "Average risk: Annual mammograms starting at age 40 (ACS recommendation)",
                "High risk (>20% lifetime): Annual mammogram + MRI starting at 30",
                "BRCA carriers: Annual mammogram + MRI starting at 25-30",
                "Clinical breast exams recommended annually for all adults",
                "Breast awareness and self-exams starting in your 20s",
                "Screening frequency may increase based on risk assessment results",
                "Discuss your personal plan with your healthcare provider",
            ],
            "resources": [
                {"name": "Screening Decision Guide by Age", "type": "guide"},
                {"name": "Risk-Based Screening Chart", "type": "reference"},
            ],
            "references": [
                "American Cancer Society 2024 Guidelines",
                "NCCN Guidelines for Breast Cancer Screening",
                "USPSTF 2024 Recommendations",
            ],
        },
        "genetic_testing": {
            "title": "Genetic Testing for Breast Cancer",
            "summary": "Genetic testing can identify inherited mutations that significantly increase breast cancer risk. Understanding your genetic status helps guide prevention and screening strategies.",
            "key_points": [
                "BRCA1 and BRCA2 mutations account for most hereditary breast cancers",
                "BRCA carriers have a 45-72% lifetime risk of breast cancer",
                "Genetic testing is recommended for those with strong family history",
                "Testing involves a simple blood or saliva sample",
                "Genetic counseling before and after testing helps interpret results",
                "Other genes (PALB2, TP53, ATM, CHEK2) also affect risk",
                "A negative test doesn't eliminate breast cancer risk entirely",
            ],
            "resources": [
                {"name": "Is Genetic Testing Right for Me?", "type": "decision_guide"},
                {"name": "Finding a Genetic Counselor", "type": "directory"},
            ],
            "references": [
                "NCCN Genetic/Familial High-Risk Assessment Guidelines",
                "National Society of Genetic Counselors",
            ],
        },
        "dense_breasts": {
            "title": "Understanding Breast Density",
            "summary": "Breast density refers to the proportion of fibrous and glandular tissue versus fatty tissue in the breast. Dense breasts are common and important because they increase cancer risk and can mask tumors on mammograms.",
            "key_points": [
                "About 40-50% of women have dense breasts",
                "Density is categorized A through D (fatty to extremely dense)",
                "Dense tissue appears white on mammograms, as do tumors",
                "Women with dense breasts may benefit from supplemental screening",
                "Breast density is determined by genetics, not breast size",
                "Many states require notification of breast density after mammogram",
                "3D mammography and MRI are more effective for dense breasts",
            ],
            "resources": [
                {"name": "Understanding Your Density Report", "type": "guide"},
                {"name": "Supplemental Screening Options", "type": "reference"},
            ],
            "references": [
                "FDA Breast Density Notification Requirements",
                "DenseBreast-info.org Educational Materials",
            ],
        },
        "lifestyle_prevention": {
            "title": "Lifestyle Factors for Breast Cancer Prevention",
            "summary": "While some risk factors can't be changed, research shows that lifestyle modifications can meaningfully reduce breast cancer risk. Small, consistent changes add up to significant protection.",
            "key_points": [
                "Regular exercise reduces risk by 10-20% (aim for 150+ minutes/week)",
                "Maintaining healthy weight reduces postmenopausal breast cancer risk",
                "Limiting alcohol to ≤1 drink/day reduces risk",
                "Breastfeeding for 12+ months provides protective benefit",
                "Quitting smoking reduces risk, especially if done before age 35",
                "Mediterranean-style diet associated with lower risk",
                "Limiting hormone therapy duration reduces associated risk",
                "Quality sleep (7-9 hours) supports overall health and immune function",
            ],
            "resources": [
                {"name": "Healthy Lifestyle Action Plan", "type": "planner"},
                {"name": "Nutrition Guide for Breast Health", "type": "guide"},
            ],
            "references": [
                "World Cancer Research Fund Prevention Guidelines",
                "American Institute for Cancer Research",
            ],
        },
        "early_detection": {
            "title": "The Importance of Early Detection",
            "summary": "Early detection of breast cancer dramatically improves outcomes. When found early (localized stage), the 5-year survival rate is 99%. Regular screening is the most effective way to catch cancer early.",
            "key_points": [
                "5-year survival rate for localized breast cancer is 99%",
                "Mammograms can find cancers too small to feel (as small as a grain of rice)",
                "Early-stage treatment is less aggressive and more effective",
                "Regular screening catches cancer an average of 1-3 years earlier",
                "Know your normal so you can recognize changes quickly",
                "Don't skip screenings - early detection saves lives",
                "Report any breast changes to your provider without delay",
            ],
            "resources": [
                {"name": "Early Detection Success Stories", "type": "testimonials"},
                {"name": "Signs and Symptoms Checklist", "type": "reference"},
            ],
            "references": [
                "American Cancer Society Survival Statistics 2024",
                "SEER Cancer Statistics Review",
            ],
        },
        "support_resources": {
            "title": "Support Resources for Your Breast Health Journey",
            "summary": "Whether you're managing screening anxiety, navigating a diagnosis, or supporting a loved one, numerous resources are available to help you through every step.",
            "key_points": [
                "Patient navigators can help coordinate appointments and insurance",
                "Support groups offer community and shared experience",
                "Financial assistance programs exist for screening and treatment",
                "Mental health support is an important part of care",
                "Helplines provide immediate information and emotional support",
                "Online communities offer 24/7 peer support",
            ],
            "resources": [
                {"name": "National Breast Cancer Helpline: 1-800-227-2345", "type": "hotline"},
                {"name": "CancerCare Financial Assistance", "type": "financial"},
                {"name": "Living Beyond Breast Cancer", "type": "support_org"},
                {"name": "Young Survival Coalition (for under 40)", "type": "support_org"},
            ],
            "references": [
                "National Cancer Institute Support Services",
                "American Cancer Society Patient Programs",
            ],
        },
        "myths_facts": {
            "title": "Breast Cancer: Myths vs. Facts",
            "summary": "Misinformation about breast cancer is common. Separating myths from facts helps you make informed decisions about your health and screening.",
            "key_points": [
                "MYTH: Only women with family history get breast cancer. FACT: 85% of cases have no family history",
                "MYTH: Mammograms cause cancer. FACT: Radiation dose is extremely low and benefits far outweigh risks",
                "MYTH: Finding a lump means you have cancer. FACT: 80% of lumps are benign",
                "MYTH: Men can't get breast cancer. FACT: About 2,800 men are diagnosed annually in the US",
                "MYTH: Antiperspirants cause breast cancer. FACT: No scientific evidence supports this claim",
                "MYTH: Small-breasted women have less risk. FACT: Breast size has no connection to cancer risk",
                "MYTH: Breast cancer is always a lump. FACT: Other signs include skin changes, discharge, and pain",
            ],
            "resources": [
                {"name": "Evidence-Based FAQ Sheet", "type": "reference"},
                {"name": "Share These Facts - Social Media Kit", "type": "awareness"},
            ],
            "references": [
                "National Cancer Institute Fact Sheets",
                "Susan G. Komen Myth vs Fact Resources",
            ],
        },
    }
