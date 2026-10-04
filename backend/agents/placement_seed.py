"""
Placement Agent — Seed Data
Run once on startup (idempotent: skips if skills already exist).
"""
from backend.database.models import Skill, RoadmapStep, Resource, Project

SKILLS = [
  {"name":"DSA","slug":"dsa","icon":"🧩","color":"#3b82f6","description":"Data Structures & Algorithms — the core of placement interviews."},
  {"name":"AI/ML","slug":"aiml","icon":"🤖","color":"#8b5cf6","description":"Machine Learning, Deep Learning, and AI fundamentals."},
  {"name":"Web Development","slug":"webdev","icon":"🌐","color":"#10b981","description":"Frontend, Backend, and Full-Stack web engineering."},
  {"name":"Data Science","slug":"datascience","icon":"📊","color":"#f59e0b","description":"Data analysis, visualisation, and statistics."},
  {"name":"Android Development","slug":"android","icon":"📱","color":"#06b6d4","description":"Native Android app development with Kotlin/Java."},
  {"name":"Cybersecurity","slug":"cybersecurity","icon":"🔐","color":"#ef4444","description":"Ethical hacking, network security, and CTF challenges."},
  {"name":"Cloud Computing","slug":"cloud","icon":"☁️","color":"#64748b","description":"AWS, GCP, Azure, serverless, and DevOps pipelines."},
  {"name":"Agentic AI","slug":"agenticai","icon":"🧠","color":"#ec4899","description":"LLM agents, RAG, LangChain, AutoGen, and multi-agent systems."},
  {"name":"DevOps","slug":"devops","icon":"⚙️","color":"#f97316","description":"CI/CD, Docker, Kubernetes, and infrastructure automation."},
  {"name":"Blockchain","slug":"blockchain","icon":"⛓️","color":"#84cc16","description":"Smart contracts, Solidity, Web3, and DeFi development."},
]

ROADMAPS = {
  "dsa": ["Arrays & Strings","Linked Lists","Stacks & Queues","Trees & BST","Graphs","Heaps & Priority Queues","Dynamic Programming","Greedy & Backtracking","System Design Basics","Interview Simulation"],
  "aiml": ["Python Basics","NumPy & Pandas","Statistics & Probability","Machine Learning (Sklearn)","Deep Learning (PyTorch)","Computer Vision","NLP & Transformers","Model Deployment","MLOps","Capstone Project"],
  "webdev": ["HTML & CSS","JavaScript ES6+","React / Vue","Node.js & Express","REST APIs","Databases (SQL + NoSQL)","Auth & Security","Deployment (Vercel/Railway)","System Design","Full-Stack Project"],
  "datascience": ["Python & Libraries","EDA & Visualisation","SQL for Data","Statistics","Feature Engineering","ML Algorithms","Time Series","Dashboards (Streamlit)","Kaggle Competitions","Capstone"],
  "android": ["Kotlin Basics","Android Studio","Layouts & UI","Activities & Intents","RecyclerView & Fragments","Jetpack Compose","Room & SQLite","REST & Retrofit","Firebase","Play Store Deployment"],
  "cybersecurity": ["Networking Basics","Linux Fundamentals","Cryptography","Web Security (OWASP)","Penetration Testing","CTF Challenges","Malware Analysis","Cloud Security","Bug Bounty","Certification Prep"],
  "cloud": ["Cloud Concepts","AWS / GCP / Azure Basics","IAM & Security","Compute & Storage","Networking in Cloud","Serverless","Containers & Kubernetes","CI/CD Pipelines","Cost Optimisation","Certification"],
  "agenticai": ["LLM Fundamentals","Prompt Engineering","LangChain Framework","RAG Architecture","Vector Databases","Multi-Agent Systems","Tool Use & Function Calling","Memory Systems","AutoGen / CrewAI","Production Deployment"],
  "devops": ["Linux & Bash","Git & Version Control","Docker","Kubernetes","CI/CD (GitHub Actions)","Infrastructure as Code","Monitoring & Logging","Cloud Integration","Security in DevOps","Capstone Pipeline"],
  "blockchain": ["Blockchain Basics","Solidity Programming","Smart Contracts","Hardhat / Foundry","ERC Standards","DeFi Protocols","NFT Development","Web3.js / Ethers.js","Security & Auditing","Capstone dApp"],
}

RESOURCES = {
  "dsa": [
    {"title":"Striver A2Z DSA Sheet","type":"practice","level":"beginner","platform":"TakeUForward","url":"https://takeuforward.org/strivers-a2z-dsa-course/","is_free":True},
    {"title":"NeetCode 150","type":"practice","level":"intermediate","platform":"NeetCode","url":"https://neetcode.io/practice","is_free":True},
    {"title":"LeetCode DSA Study Plan","type":"practice","level":"intermediate","platform":"LeetCode","url":"https://leetcode.com/study-plan/data-structure/","is_free":True},
    {"title":"Striver DSA Playlist","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/takeUforward","is_free":True},
    {"title":"Abdul Bari Algorithms","type":"youtube","level":"intermediate","platform":"YouTube","url":"https://www.youtube.com/watch?v=0IAPZzGSbME&list=PLAXnLdrLnQpRcveZTtD644gM9uzYqJCwr","is_free":True},
    {"title":"GeeksForGeeks DSA","type":"article","level":"beginner","platform":"GFG","url":"https://www.geeksforgeeks.org/data-structures/","is_free":True},
  ],
  "aiml": [
    {"title":"Andrew Ng ML Specialisation","type":"course","level":"beginner","platform":"Coursera","url":"https://www.coursera.org/specializations/machine-learning-introduction","is_free":False},
    {"title":"Google ML Crash Course","type":"course","level":"beginner","platform":"Google","url":"https://developers.google.com/machine-learning/crash-course","is_free":True},
    {"title":"Fast.ai Deep Learning","type":"course","level":"intermediate","platform":"Fast.ai","url":"https://course.fast.ai/","is_free":True},
    {"title":"DeepLearning.AI Specialisation","type":"course","level":"intermediate","platform":"Coursera","url":"https://www.coursera.org/specializations/deep-learning","is_free":False},
    {"title":"StatQuest with Josh Starmer","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/joshstarmer","is_free":True},
    {"title":"Sentdex ML Tutorials","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/sentdex","is_free":True},
    {"title":"Kaggle ML Courses","type":"course","level":"beginner","platform":"Kaggle","url":"https://www.kaggle.com/learn","is_free":True},
  ],
  "webdev": [
    {"title":"The Odin Project","type":"course","level":"beginner","platform":"Odin Project","url":"https://www.theodinproject.com/","is_free":True},
    {"title":"Full Stack Open (Helsinki)","type":"course","level":"intermediate","platform":"University of Helsinki","url":"https://fullstackopen.com/","is_free":True},
    {"title":"Traversy Media React Crash","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/watch?v=LDB4uaJ87e0","is_free":True},
    {"title":"Fireship.io","type":"youtube","level":"intermediate","platform":"YouTube","url":"https://www.youtube.com/c/Fireship","is_free":True},
    {"title":"MDN Web Docs","type":"article","level":"beginner","platform":"Mozilla","url":"https://developer.mozilla.org/","is_free":True},
  ],
  "datascience": [
    {"title":"Kaggle Data Science Courses","type":"course","level":"beginner","platform":"Kaggle","url":"https://www.kaggle.com/learn/data-science","is_free":True},
    {"title":"IBM Data Science Professional","type":"course","level":"intermediate","platform":"Coursera","url":"https://www.coursera.org/professional-certificates/ibm-data-science","is_free":False},
    {"title":"Ken Jee Data Science Project","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/KenJee1","is_free":True},
  ],
  "android": [
    {"title":"Android Basics in Kotlin","type":"course","level":"beginner","platform":"Google","url":"https://developer.android.com/courses/android-basics-kotlin","is_free":True},
    {"title":"Philipp Lackner Android","type":"youtube","level":"intermediate","platform":"YouTube","url":"https://www.youtube.com/c/PhilippLackner","is_free":True},
  ],
  "cybersecurity": [
    {"title":"TryHackMe","type":"practice","level":"beginner","platform":"TryHackMe","url":"https://tryhackme.com/","is_free":True},
    {"title":"HackTheBox","type":"practice","level":"intermediate","platform":"HackTheBox","url":"https://www.hackthebox.com/","is_free":True},
    {"title":"NetworkChuck","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/NetworkChuck","is_free":True},
  ],
  "cloud": [
    {"title":"AWS Cloud Practitioner (free)","type":"course","level":"beginner","platform":"AWS","url":"https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/","is_free":True},
    {"title":"Google Cloud Skills Boost","type":"course","level":"beginner","platform":"Google","url":"https://cloudskillsboost.google/","is_free":True},
    {"title":"TechWorld with Nana","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/TechWorldwithNana","is_free":True},
  ],
  "agenticai": [
    {"title":"LangChain Docs","type":"article","level":"intermediate","platform":"LangChain","url":"https://python.langchain.com/","is_free":True},
    {"title":"DeepLearning.AI LangChain Course","type":"course","level":"intermediate","platform":"DeepLearning.AI","url":"https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/","is_free":True},
    {"title":"AutoGen Microsoft","type":"article","level":"advanced","platform":"Microsoft","url":"https://microsoft.github.io/autogen/","is_free":True},
  ],
  "devops": [
    {"title":"TechWorld with Nana DevOps","type":"youtube","level":"beginner","platform":"YouTube","url":"https://www.youtube.com/c/TechWorldwithNana","is_free":True},
    {"title":"KodeKloud DevOps","type":"course","level":"intermediate","platform":"KodeKloud","url":"https://kodekloud.com/","is_free":False},
  ],
  "blockchain": [
    {"title":"CryptoZombies","type":"course","level":"beginner","platform":"CryptoZombies","url":"https://cryptozombies.io/","is_free":True},
    {"title":"Patrick Collins Solidity","type":"youtube","level":"intermediate","platform":"YouTube","url":"https://www.youtube.com/c/PatrickCollins","is_free":True},
  ],
}

PROJECTS = {
  "dsa": [
    {"title":"LeetCode 100 Challenge","difficulty":"beginner","skills":["Arrays","Strings","Recursion"],"github":"https://github.com/topics/leetcode","outcomes":["Problem solving speed","Pattern recognition"]},
    {"title":"Graph Pathfinder Visualiser","difficulty":"intermediate","skills":["Graphs","BFS","DFS"],"github":"https://github.com/topics/graph-algorithm","outcomes":["Algorithm visualisation","Web integration"]},
    {"title":"Competitive Programming Bot","difficulty":"advanced","skills":["DP","Graphs","Trees"],"github":"https://github.com/topics/competitive-programming","outcomes":["Advanced optimisation"]},
  ],
  "aiml": [
    {"title":"House Price Prediction","difficulty":"beginner","skills":["Python","Pandas","Sklearn"],"github":"https://github.com/topics/house-price-prediction","outcomes":["Regression","EDA"]},
    {"title":"Resume Analyser","difficulty":"intermediate","skills":["NLP","spaCy","Flask"],"github":"https://github.com/topics/resume-parser","outcomes":["NLP pipeline","API design"]},
    {"title":"AI Career Mentor (Multi-Agent)","difficulty":"advanced","skills":["LLM","LangChain","RAG"],"github":"https://github.com/topics/langchain","outcomes":["Agent orchestration","Production AI"]},
  ],
  "webdev": [
    {"title":"Portfolio Website","difficulty":"beginner","skills":["HTML","CSS","JS"],"github":"https://github.com/topics/portfolio","outcomes":["UI design","Deployment"]},
    {"title":"E-Commerce Platform","difficulty":"intermediate","skills":["React","Node.js","MongoDB"],"github":"https://github.com/topics/ecommerce","outcomes":["Full-stack development","Auth"]},
    {"title":"Real-Time Collaboration Tool","difficulty":"advanced","skills":["WebSockets","Redis","React"],"github":"https://github.com/topics/collaborative","outcomes":["Real-time systems","Scalability"]},
  ],
  "datascience": [
    {"title":"COVID-19 Dashboard","difficulty":"beginner","skills":["Python","Plotly","Pandas"],"github":"https://github.com/topics/covid-dashboard","outcomes":["Data viz","EDA"]},
    {"title":"Customer Churn Prediction","difficulty":"intermediate","skills":["ML","Feature Engineering"],"github":"https://github.com/topics/churn-prediction","outcomes":["Classification","Business insight"]},
  ],
  "android": [
    {"title":"To-Do App","difficulty":"beginner","skills":["Kotlin","Room","Jetpack Compose"],"github":"https://github.com/topics/todo-android","outcomes":["CRUD","UI components"]},
    {"title":"Fitness Tracker App","difficulty":"intermediate","skills":["Kotlin","Firebase","Charts"],"github":"https://github.com/topics/fitness-app","outcomes":["Sensor APIs","Cloud sync"]},
  ],
  "cybersecurity": [
    {"title":"Port Scanner in Python","difficulty":"beginner","skills":["Python","Sockets"],"github":"https://github.com/topics/port-scanner","outcomes":["Network fundamentals"]},
    {"title":"CTF Challenge Writeups","difficulty":"intermediate","skills":["Linux","Cryptography"],"github":"https://github.com/topics/ctf-writeups","outcomes":["Security mindset"]},
  ],
  "cloud": [
    {"title":"Deploy App on AWS EC2","difficulty":"beginner","skills":["AWS","Linux","Nginx"],"github":"https://github.com/topics/aws-ec2","outcomes":["Cloud deployment"]},
    {"title":"Serverless REST API","difficulty":"intermediate","skills":["AWS Lambda","API Gateway","DynamoDB"],"github":"https://github.com/topics/serverless","outcomes":["Serverless architecture"]},
  ],
  "agenticai": [
    {"title":"RAG Q&A Chatbot","difficulty":"beginner","skills":["LangChain","FAISS","OpenAI"],"github":"https://github.com/topics/rag","outcomes":["Vector search","LLM integration"]},
    {"title":"Multi-Agent Research Assistant","difficulty":"advanced","skills":["AutoGen","LangGraph","Tools"],"github":"https://github.com/topics/multi-agent","outcomes":["Agent orchestration"]},
  ],
  "devops": [
    {"title":"Dockerise a Web App","difficulty":"beginner","skills":["Docker","Nginx"],"github":"https://github.com/topics/docker","outcomes":["Containerisation"]},
    {"title":"CI/CD Pipeline with GitHub Actions","difficulty":"intermediate","skills":["GitHub Actions","Docker","AWS"],"github":"https://github.com/topics/github-actions","outcomes":["Automation","DevOps culture"]},
  ],
  "blockchain": [
    {"title":"Simple Token (ERC-20)","difficulty":"beginner","skills":["Solidity","Hardhat"],"github":"https://github.com/topics/erc20","outcomes":["Smart contract basics"]},
    {"title":"NFT Marketplace","difficulty":"intermediate","skills":["Solidity","React","Ethers.js"],"github":"https://github.com/topics/nft-marketplace","outcomes":["Full dApp development"]},
  ],
}


def seed_placement_data(db):
    """Seed all skills idempotently. Call from init_db or startup."""
    from sqlalchemy.orm import Session
    existing = db.query(Skill).count()
    if existing >= len(SKILLS):
        return  # already seeded

    slug_map: dict = {}
    for s in SKILLS:
        skill = db.query(Skill).filter_by(slug=s["slug"]).first()
        if not skill:
            skill = Skill(name=s["name"], slug=s["slug"], icon=s["icon"],
                          color=s["color"], description=s["description"])
            db.add(skill)
            db.flush()
        slug_map[s["slug"]] = skill

        # Roadmap steps
        existing_steps = db.query(RoadmapStep).filter_by(skill_id=skill.id).count()
        if existing_steps == 0:
            for i, step_name in enumerate(ROADMAPS.get(s["slug"], []), start=1):
                db.add(RoadmapStep(skill_id=skill.id, step_order=i, step_name=step_name,
                                   description=f"Master {step_name}", estimated_days=7))

        # Resources
        existing_res = db.query(Resource).filter_by(skill_id=skill.id).count()
        if existing_res == 0:
            for r in RESOURCES.get(s["slug"], []):
                db.add(Resource(skill_id=skill.id, title=r["title"],
                                resource_type=r["type"], level=r["level"],
                                platform=r["platform"], url=r["url"],
                                is_free=r.get("is_free", True)))

        # Projects
        existing_proj = db.query(Project).filter_by(skill_id=skill.id).count()
        if existing_proj == 0:
            for p in PROJECTS.get(s["slug"], []):
                db.add(Project(skill_id=skill.id, title=p["title"],
                               difficulty=p["difficulty"],
                               skills_required=p.get("skills", []),
                               github_url=p.get("github", ""),
                               learning_outcomes=p.get("outcomes", [])))
    db.commit()
    print(f"[Seed] Placement data seeded: {len(SKILLS)} skills.")
