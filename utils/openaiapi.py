import json
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
client = OpenAI()

async def user_response(user_input):
    """Extract 5 Keywords from user prompt"""
    completion = client.chat.completions.create(
    model="gpt-4o-mini-2024-07-18",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Extract the 5 keywords from the user text input that could help search engine to find helpful resource relevant to user input. only provide me text response no numerical values"},
        {"role": "user", "content": user_input}
    ]
    )

    #print(completion.choices[0].message.content)
    return completion.choices[0].message.content
async def show_notes(transcript_value):
    """Show notes of Micro Podcast"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in podcast communication and asked to create show notes for this podcast transcript. Your task is to analyze the transcript and create comprehensive show notes that enhance listener engagement and accessibility. Here are the details you need to include in the show notes: Title: Devise an engaging and descriptive title for the podcast episode based on the main themes discussed. Introduction or Summary: Summarize the podcast succinctly in no more than two sentences, capturing the essence and main points of the discussion. Guest Information: Provide a list of any guests mentioned in the podcast. If there are no additional guests, please note 'No additional guests.' Key Takeaways: Identify at least three key takeaways from the podcast. Each takeaway should be insightful and listed with a small check mark. Mentioned Resources and Links: Compile a list of any books, articles, websites, or other resources mentioned during the podcast. Include links to these resources if available. If no external references were made, state 'No outside links or resources.' Quotes or Highlights: Extract and list at least two engaging quotes or significant highlights from the podcast. Ensure these quotes encapsulate key moments or statements and place them in quotes. Contact Information: For further inquiries or more information, provide the email contact as dan@rockettools.io. Ensure the show notes are clear, informative, and formatted for easy reading, catering to both current listeners and potential new subscribers.",
                },
                {"role": "user", "content": transcript_value}
            ]
        )
        res = completion.choices[0].message.content
        return res
    except Exception as e:
        return {"error": str(e)}
    
    
async def create_podcast_script(transcript_value):
    #"""Create script for Micro Podcast"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are tasked with converting a transcript of notes into a script for a compelling and engaging business and marketing podcast. The goal is to create a podcast that is approximately 3 1/2 minutes when read at a natural podcast speed. The speaker in the podcast is Dan McCoy, and the podcast is titled \"The Ignition by RocketTools Podcast.\" This script should be written in the first person, as if Dan is delivering it directly to the audience. Follow these guidelines to ensure the script is both informative and entertaining: **Introduction (Hook):** - Start with an engaging hook that immediately grabs attention—this could be a thought-provoking question, an intriguing fact, or a bold statement relevant to the podcast’s main topic. **Body (Flow of Information):** - **Segment 1:** Introduce the main topic with a concise overview of the key points to be covered, setting the stage for the detailed discussion that will follow. - **Segment 2:** Elaborate on the first key point. Clearly present the information and integrate compelling quotes to highlight critical insights. Enhance the narrative with anecdotes or relevant data to maintain listener interest. - **Segment 3 and Beyond:** Continue with subsequent points, ensuring seamless transitions between segments. Maintain engagement by incorporating expert opinions, quotes, and real-life examples throughout these sections. **Conclusion:** - Recap the main points discussed, emphasizing the overarching theme. Summarize the key takeaways and reflect on the implications or future perspectives. - End with a call to action, encouraging listeners to like and subscribe, and inviting them to engage further through comments or social media. **Additional Guidelines:** - Ensure the script is conversational, clear, and direct, avoiding jargon and technical terms to keep it accessible and engaging. - Include natural pauses after significant points for emphasis. - Only return the actual script—no introduction comments or additional formatting. This means no transitions, time stamps, or any other introductory text. The output should be nothing except the script so that it can be directly read by the user with no other content, quotation marks, or other text. - Avoid including timestamps. **Style Note:** - Avoid using common AI-sounding words like unleash, unlock, delve, dive, treasure trove, game changer, maximize, revolutionize, status quo, imagine, picture, etc. - The script should start with a compelling hook and use natural transitions. Avoid overusing words like \"next\" or \"Let’s move on.\" Here is an example script for style reference only. Do not use any of these details in the podcast, but follow this language style: Dan (00:04) I'm a storytelling consultant. That always confuses people, but we help companies tell stories. This can be a revamp of strategy, a product idea that gets articulated into a business solution or a simple marketing message. If you can't communicate your idea, then your idea is relatively useless and it will be lost. If you tell your story, well, then your idea gains instant value. It's that simple. Today in about three and a half minutes or less, we're going to talk about the Zippo lighter, the power of hands -on storytelling, and how the digital world revolutionizes building things. When you talk about solving problems, you wouldn't naturally think about fire. It's been around a long time, and we've moved way past rubbing two sticks together. In 1932, George G. Bladestell of Bradford, Pennsylvania, observed a friend struggling with an Austrian -made lighter. While effective in wind, it was very cumbersome to use. Bladzell saw an opportunity. He acquired rights to the lighter's windproof chimney and reimagined the design. The result was a rectangular case with a hinged lid, operable with one hand. This simple yet revolutionary change became Zippo's hallmark. In any story, there are three basic elements. Headline, proof points, and the anecdotal story. There is no better proof point than a physical product. When you take an idea and convert it into something you can show and pass around, you turn mere thoughts into something real, and you immediately turn authenticity into trust. In a moment, your story prospects turn into believers. and the first big challenge of selling an idea has been eliminated. That's why I often tell entrepreneurs to put in the time and effort to create an example of what they are creating. That can be with parts from True Value or with Canva. It doesn't matter. Create an object that people can see, touch, demonstrate, play with, and even break. It proves two things, that you have a real product and not just an idea. And more importantly, that you have the ability to build it. Plus, as a bonus, nothing works well the first time, so getting started on version one of a product just accelerates the entire process. This is the greatest age for makers. So definition, what is a maker? A maker typically refers to a person who engages in the creation of items, often using their hands or tools. This can include a wide range of activities, such as crafting, building, DIY projects, electronics, woodworking, metalworking, software development, and much more. Makers often belong to a community and share their projects, ideas, and tools, embodying a spirit of creativity, innovation, and resourcefulness. With the advent of AI, there has been a democratization of the maker space. Today, you can have an idea and with a simple no -code web -based program, You can interconnect elements to create a physical product that solves a problem. I recently observed a seasoned CEO learn an entirely new no code programming language and get his hands dirty building a minimal viable product. He wasn't a programmer. He knew the problem he wanted to solve and he was motivated enough to put the effort into creating a physical solution. And that sells. You can create amazing PowerPoint decks and artifacts for investors, nothing replaces having a demonstrable solution. So get your hands dirty and become a maker. Here is the content to enrich and turn into a podcast"
                },
                {"role": "user", "content": transcript_value}
            ]
        )
        res =  completion.choices[0].message.content
        return res
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


async def transcription_prose(transcribed_value: str, text:str):
    """Generates transcription for RocketProse"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert in transcript generation. Create a concise and brief transcript using '{text}'content provided by the user.",
                },
                {"role": "user", "content": transcribed_value}
            ]
        )
        res = completion.choices[0].message.content
        print("openai response trnascript", res)
        return {"transcribed_text": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate transcription: {e}")

