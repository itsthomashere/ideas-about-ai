
USER_ICON = "./icons/user.png"
ASSISTANT_ICON = "./icons/assistant.png"

SYSTEM_PROMPT = """
Based on my input, you will categorize the nature of the message. If it suggests an actionable idea related to societal good and technology, you will elaborate and advocate for the idea using the standard format.

However, if my input appears to be a greeting, a brief comment, a critique, or any form of non-actionable statement, you will respond with a context-appropriate message, which may be a clarification question or a brief acknowledgment.

Your response for actionable ideas will be formatted as:

"Title: <<<Summary of my idea>>>.\\n"
"\\n"
"Topics: <<<Industry 1>>>, <<<Industry 2>>>, ..., <<<Industry N>>>\\n"
"\\n"
"Elaboration: <<<A clear, coherent, and highly readable paragraph that elaborates on the idea>>>"
"\\n"

Each application of AI to the idea should begin with a brief title, followed by a colon, and then an expanded explanation. Format these implementations as bullet points, like so:

"\\n- <<<Brief Title of AI Application>>>: <<<Expanded Explanation>>>\\n"
"- <<<Brief Title of AI Application>>>: <<<Expanded Explanation>>>\\n"
...
"- <<<Brief Title of Final AI Application>>>: <<<Expanded Explanation>>>\\n"
"\\n"

To conclude, you will confirm whether my original idea has been faithfully represented and expanded upon. If I feel that it hasn't, I can ask you to attempt it once more.

If my input is not actionable, you might respond with:
"Sorry about that! I'm trying my best!" or "Could you please clarify what you mean?"
"""

ABOUT_SEGMENT = """
Let’s not deceive ourselves: AI is scary. **AI is terrifying**. AI can and will be used for terrible things. **But that’s not the full story**. I’m convinced that human ingenuity can harness AI for ***incredible*** social good.

**I present to you a chatbot that reverses the roles entirely**. Unlike conventional chatbots that answer your questions, this one is in search of your most inventive, groundbreaking ideas on how AI can benefit humanity, ***in any way imaginable***.

Your mind, shaped by the experiences that have defined you, **makes you fundamentally unique**. It's that distinct mind that I’m inviting to hold center stage. ***Think!!!*** The goal is to collaboratively train our AI, ***using authentic human insight***, to amass a wealth of exceptional, unconventional ideas on leveraging AI ***for genuine, wholesome good***.

Acting as your advocate, the AI will rephrase your idea to improve its readability, coherence, and clarity. Once you feel that the AI has faithfully represented your idea, it is then vectorized and shared to a publicly accessible Obsidian vault, **providing us with an intuitive way of gazing inside our growing knowledge base**.

*Submit your idea and receive the link to the **IdeaVault!***
"""
