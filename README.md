AI Study Pack Generator

A staged AI workflow application that creates personalized study packs.

AI Workflow

Student Profile
      |
      v
[1] Planning
      |
      | plan + student context
      v
[2] Content Generation
      |
      | content + plan + student context
      v
[3] Assessment
      |
      | quality score + issues
      v
[4] Review
      |
      | prioritized fixes
      v
[5] Refinement
      |
      | revised content
      v
Final Study Pack

If the assessment does not reach the quality threshold, the workflow can run
up to two refinement rounds.

Features

Personalized study planning

AI-generated summaries

Key points

Flashcards

MCQs

Short questions

Long questions

Study tips

Automated AI quality assessment

Review and refinement loop

Context passing between stages

Retry/error handling

Downloadable study pack

Streamlit deployment

Run locally

pip install -r requirements.txt
streamlit run app.py

Create .streamlit/secrets.toml:

GROQ_API_KEY = "your-groq-api-key"

Do not commit this file.

Deploy

Push app.py and requirements.txt to GitHub, then deploy the repository
with Streamlit Community Cloud. Add GROQ_API_KEY under the app's Secrets
settings.