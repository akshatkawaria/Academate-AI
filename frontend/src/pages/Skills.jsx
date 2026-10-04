import { useState, useEffect } from 'react';
import { Brain, AlertCircle, BookOpen } from 'lucide-react';
import SkillSearch from '../components/skills/SkillSearch';
import StudentProfileCard from '../components/skills/StudentProfileCard';
import SkillOverviewCard from '../components/skills/SkillOverviewCard';
import RoadmapTimeline from '../components/skills/RoadmapTimeline';
import ResourceCards from '../components/skills/ResourceCards';
import ProjectCards from '../components/skills/ProjectCards';
import PlacementTips from '../components/skills/PlacementTips';
import { generateSkillRoadmap, getStudentProfile, updateStudentProfile, checkSkillExists } from '../services/skillService';


// ══════════════════════════════════════════════════════════
// MOCK DATA — Replace with API calls later
// ══════════════════════════════════════════════════════════

const MOCK_STUDENT = {
  name: 'Akshat',
  year: '2nd Year',
  target_role: 'AI Engineer',
  daily_hours: 4,
};

const MOCK_SKILLS = {
  RAG: {
    skill_name: 'RAG (Retrieval-Augmented Generation)',
    category: 'AI / GenAI',
    difficulty: 'Intermediate',
    estimated_duration: '2-3 Months',
    prerequisites: 'Python, LLM Basics, Vector Databases',
    career_benefits: 'High demand in GenAI and enterprise AI applications. Essential for building production-grade AI systems.',
    roadmap: 'Fundamentals → Embeddings → Vector DBs → LangChain → Production RAG',
    project_ideas: 'PDF Chatbot, Research Assistant, Knowledge Base QA',
  },
  NLP: {
    skill_name: 'Natural Language Processing',
    category: 'AI / ML',
    difficulty: 'Intermediate',
    estimated_duration: '3-4 Months',
    prerequisites: 'Python, Linear Algebra, Probability',
    career_benefits: 'Core skill for AI/ML roles. Powers chatbots, search engines, and content analysis.',
    roadmap: 'Text Processing → Word Embeddings → Transformers → Fine-tuning → Deployment',
    project_ideas: 'Sentiment Analyzer, Text Summarizer, Named Entity Recognition',
  },
  React: {
    skill_name: 'React.js',
    category: 'Frontend Development',
    difficulty: 'Beginner',
    estimated_duration: '1-2 Months',
    prerequisites: 'HTML, CSS, JavaScript',
    career_benefits: 'Most in-demand frontend framework. Used by top companies globally.',
    roadmap: 'JSX → Components → State → Hooks → Routing → State Management',
    project_ideas: 'Dashboard App, E-commerce UI, Social Media Clone',
  },
  'Agentic AI': {
    skill_name: 'Agentic AI',
    category: 'AI / Advanced',
    difficulty: 'Advanced',
    estimated_duration: '3-5 Months',
    prerequisites: 'Python, LLM APIs, Prompt Engineering, RAG',
    career_benefits: 'Cutting-edge field with massive industry demand. Key to building autonomous AI systems.',
    roadmap: 'LLM Basics → Tool Use → Agent Frameworks → Multi-Agent Systems → Production',
    project_ideas: 'Auto-Researcher Agent, Code Review Agent, Customer Support Agent',
  },
};

const MOCK_LEARNING_PLANS = {
  RAG: [
    {
      week: 1,
      focus: 'Foundations of RAG & Embeddings',
      tasks: ['Understand what RAG is and why it matters', 'Learn about text embeddings (Word2Vec, Sentence Transformers)', 'Set up Python environment with LangChain'],
      resources: ['LangChain Documentation', 'Sentence Transformers Guide'],
    },
    {
      week: 2,
      focus: 'Vector Databases & Retrieval',
      tasks: ['Learn Pinecone / ChromaDB / FAISS', 'Build a basic vector store from documents', 'Implement similarity search'],
      resources: ['ChromaDB Quickstart', 'FAISS Tutorial'],
    },
    {
      week: 3,
      focus: 'Building RAG Pipelines',
      tasks: ['Connect retriever to LLM using LangChain', 'Implement document chunking strategies', 'Build a complete RAG pipeline'],
      resources: ['LangChain RAG Tutorial', 'OpenAI Cookbook'],
    },
    {
      week: 4,
      focus: 'Advanced RAG & Production',
      tasks: ['Learn advanced techniques (HyDE, reranking, hybrid search)', 'Evaluate RAG performance with RAGAS', 'Deploy a RAG application'],
      resources: ['RAGAS Documentation', 'LangSmith Tracing'],
    },
  ],
  NLP: [
    {
      week: 1,
      focus: 'Text Processing Fundamentals',
      tasks: ['Learn tokenization, stemming, lemmatization', 'Understand TF-IDF and Bag of Words', 'Practice with NLTK and spaCy'],
      resources: ['NLTK Documentation', 'spaCy 101'],
    },
    {
      week: 2,
      focus: 'Word Embeddings & Representations',
      tasks: ['Study Word2Vec, GloVe, FastText', 'Implement embedding visualizations', 'Understand contextual embeddings'],
      resources: ['Stanford NLP Course', 'Gensim Tutorials'],
    },
    {
      week: 3,
      focus: 'Transformer Architecture',
      tasks: ['Learn attention mechanism', 'Understand BERT, GPT architectures', 'Fine-tune a pre-trained model'],
      resources: ['Hugging Face Course', 'Illustrated Transformer'],
    },
    {
      week: 4,
      focus: 'NLP Applications & Deployment',
      tasks: ['Build a sentiment analysis pipeline', 'Create a text classification model', 'Deploy with FastAPI'],
      resources: ['Hugging Face Hub', 'FastAPI Documentation'],
    },
  ],
  React: [
    {
      week: 1,
      focus: 'React Fundamentals',
      tasks: ['Learn JSX syntax and component structure', 'Understand props and state', 'Build simple interactive components'],
      resources: ['React Official Docs', 'Vite Setup Guide'],
    },
    {
      week: 2,
      focus: 'Hooks & State Management',
      tasks: ['Master useState, useEffect, useRef', 'Learn custom hooks', 'Implement form handling'],
      resources: ['React Hooks Guide', 'Dan Abramov Blog'],
    },
    {
      week: 3,
      focus: 'Routing & API Integration',
      tasks: ['Set up React Router', 'Fetch data from APIs with useEffect', 'Handle loading and error states'],
      resources: ['React Router Docs', 'Axios Documentation'],
    },
    {
      week: 4,
      focus: 'Advanced Patterns & Deployment',
      tasks: ['Learn Context API / Zustand', 'Implement code splitting', 'Deploy to Vercel or Netlify'],
      resources: ['Zustand Documentation', 'Vercel Deployment Guide'],
    },
  ],
  'Agentic AI': [
    {
      week: 1,
      focus: 'LLM APIs & Prompt Engineering',
      tasks: ['Master OpenAI / Gemini API calls', 'Learn structured output and function calling', 'Understand prompt chaining'],
      resources: ['OpenAI API Docs', 'Prompt Engineering Guide'],
    },
    {
      week: 2,
      focus: 'Tool Use & Function Calling',
      tasks: ['Implement tool-augmented LLMs', 'Build agents with web search, code execution', 'Learn ReAct pattern'],
      resources: ['LangChain Agents Docs', 'ReAct Paper'],
    },
    {
      week: 3,
      focus: 'Agent Frameworks (LangGraph / CrewAI)',
      tasks: ['Build stateful agents with LangGraph', 'Implement multi-agent collaboration', 'Add memory and persistence'],
      resources: ['LangGraph Documentation', 'CrewAI Quickstart'],
    },
    {
      week: 4,
      focus: 'Production Agent Systems',
      tasks: ['Implement guardrails and safety', 'Add observability with LangSmith', 'Deploy agent as an API service'],
      resources: ['LangSmith Docs', 'Agent Best Practices Guide'],
    },
  ],
};

const MOCK_RESOURCES = {
  RAG: [
    { title: 'LangChain Documentation', type: 'Documentation', difficulty: 'Intermediate', url: 'https://python.langchain.com/' },
    { title: 'RAG from Scratch - YouTube', type: 'Video', difficulty: 'Beginner', url: 'https://youtube.com' },
    { title: 'ChromaDB Quickstart', type: 'Tutorial', difficulty: 'Beginner', url: 'https://docs.trychroma.com/' },
    { title: 'Advanced RAG Techniques', type: 'Course', difficulty: 'Advanced', url: 'https://deeplearning.ai' },
  ],
  NLP: [
    { title: 'Hugging Face NLP Course', type: 'Course', difficulty: 'Intermediate', url: 'https://huggingface.co/learn/nlp-course' },
    { title: 'spaCy 101', type: 'Documentation', difficulty: 'Beginner', url: 'https://spacy.io/usage/spacy-101' },
    { title: 'Stanford CS224N', type: 'Course', difficulty: 'Advanced', url: 'https://web.stanford.edu/class/cs224n/' },
  ],
  React: [
    { title: 'React Official Documentation', type: 'Documentation', difficulty: 'Beginner', url: 'https://react.dev' },
    { title: 'Full React Tutorial', type: 'Video', difficulty: 'Beginner', url: 'https://youtube.com' },
    { title: 'React TypeScript Cheatsheet', type: 'Documentation', difficulty: 'Intermediate', url: 'https://react-typescript-cheatsheet.netlify.app/' },
  ],
  'Agentic AI': [
    { title: 'LangGraph Documentation', type: 'Documentation', difficulty: 'Advanced', url: 'https://langchain-ai.github.io/langgraph/' },
    { title: 'Building AI Agents - DeepLearning.AI', type: 'Course', difficulty: 'Intermediate', url: 'https://deeplearning.ai' },
    { title: 'CrewAI Framework', type: 'Tutorial', difficulty: 'Intermediate', url: 'https://www.crewai.com/' },
  ],
};

const MOCK_PROJECTS = {
  RAG: [
    { name: 'PDF Chatbot', difficulty: 'Beginner', description: 'Build a chatbot that can answer questions from uploaded PDFs using embeddings and vector search.' },
    { name: 'Research Paper Assistant', difficulty: 'Intermediate', description: 'Create an assistant that answers questions from academic research papers with citation support.' },
    { name: 'Enterprise Knowledge Base', difficulty: 'Advanced', description: 'Build a production RAG system with multi-source ingestion, reranking, and evaluation metrics.' },
  ],
  NLP: [
    { name: 'Sentiment Dashboard', difficulty: 'Beginner', description: 'Build a web dashboard that analyzes sentiment of product reviews in real-time.' },
    { name: 'Text Summarizer API', difficulty: 'Intermediate', description: 'Create a REST API that summarizes long articles using transformer models.' },
  ],
  React: [
    { name: 'Task Manager App', difficulty: 'Beginner', description: 'Build a beautiful task management app with drag-and-drop, categories, and local storage.' },
    { name: 'Real-time Dashboard', difficulty: 'Intermediate', description: 'Create a live analytics dashboard with charts, filters, and WebSocket data updates.' },
  ],
  'Agentic AI': [
    { name: 'Auto-Research Agent', difficulty: 'Intermediate', description: 'Build an agent that autonomously researches a topic, synthesizes information, and generates reports.' },
    { name: 'Code Review Agent', difficulty: 'Advanced', description: 'Create a multi-agent system that reviews code, suggests improvements, and generates tests.' },
  ],
};

const MOCK_TIPS = {
  RAG: [
    'Build at least 2 portfolio projects using RAG pipelines',
    'Learn vector databases deeply (Pinecone, ChromaDB, Weaviate)',
    'Understand embeddings and similarity metrics',
    'Practice explaining RAG architecture in interviews',
    'Add your RAG projects to GitHub with proper README files',
    'Learn evaluation frameworks like RAGAS for measuring RAG quality',
  ],
  NLP: [
    'Master the Transformer architecture inside-out',
    'Build projects using Hugging Face models',
    'Understand tokenization strategies and their impact',
    'Practice NLP system design interview questions',
    'Contribute to open-source NLP projects',
  ],
  React: [
    'Build a portfolio website showcasing your React projects',
    'Master state management (Context API, Zustand, Redux)',
    'Practice building responsive, accessible components',
    'Learn testing with React Testing Library',
    'Deploy projects to Vercel for live demos',
  ],
  'Agentic AI': [
    'Build and showcase multi-agent systems in your portfolio',
    'Understand prompt engineering deeply',
    'Learn about safety, guardrails, and responsible AI',
    'Practice explaining agent architectures in interviews',
    'Stay updated with LangGraph, CrewAI, and AutoGen frameworks',
  ],
};


// ══════════════════════════════════════════════════════════
// LOADING SKELETON
// ══════════════════════════════════════════════════════════

function SkeletonLoader() {
  return (
    <div style={{ animation: 'skFadeIn 0.3s ease' }}>
      <div className="sk-grid-top">
        <div className="sk-skeleton-card">
          <div className="sk-skeleton-circle" />
          <div className="sk-skeleton-line" />
          <div className="sk-skeleton-line sk-skeleton-line-short" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16 }}>
            <div className="sk-skeleton-line" style={{ height: 60 }} />
            <div className="sk-skeleton-line" style={{ height: 60 }} />
          </div>
        </div>
        <div className="sk-skeleton-card">
          <div className="sk-skeleton-line sk-skeleton-line-medium" style={{ height: 20 }} />
          <div className="sk-skeleton-line sk-skeleton-line-short" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginTop: 16 }}>
            <div className="sk-skeleton-line" style={{ height: 50 }} />
            <div className="sk-skeleton-line" style={{ height: 50 }} />
          </div>
          <div className="sk-skeleton-line" style={{ marginTop: 16 }} />
          <div className="sk-skeleton-line sk-skeleton-line-medium" />
        </div>
      </div>

      <div className="sk-skeleton-card" style={{ marginBottom: 24 }}>
        <div className="sk-skeleton-line sk-skeleton-line-short" style={{ height: 20, marginBottom: 24 }} />
        {[1, 2, 3, 4].map(i => (
          <div key={i} style={{ display: 'flex', gap: 16, marginBottom: 24, paddingLeft: 32 }}>
            <div>
              <div className="sk-skeleton-line sk-skeleton-line-short" />
              <div className="sk-skeleton-line" style={{ height: 18 }} />
              <div className="sk-skeleton-line sk-skeleton-line-medium" />
              <div className="sk-skeleton-line sk-skeleton-line-medium" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// ══════════════════════════════════════════════════════════
// MAIN PAGE COMPONENT
// ══════════════════════════════════════════════════════════

export default function Skills() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null); // { skill, student, learningPlan, resources, projects, tips }

  const [step, setStep] = useState('search'); // 'search', 'profile_form', 'loading', 'results'
  const [loadingText, setLoadingText] = useState('Generating...');
  const [profile, setProfile] = useState({
    name: 'Akshat',
    year: '2nd Year',
    target_role: 'AI Engineer',
    daily_hours: 4,
  });
  const [profileForm, setProfileForm] = useState({
    name: '',
    year: '2nd Year',
    target_role: '',
    daily_hours: 4,
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const studentData = await getStudentProfile(1);
        if (studentData) {
          setProfile(studentData);
        }
      } catch (err) {
        console.error("Failed to fetch student profile", err);
      }
    };
    fetchProfile();
  }, []);

  const handleGenerate = async () => {
    const skill = query.trim();
    if (!skill) return;

    // Check Mock Data
    const matchKey = Object.keys(MOCK_SKILLS).find(
      k => k.toLowerCase() === skill.toLowerCase()
    );

    if (matchKey) {
      setLoadingText("Generating...");
      setProfileForm({
        name: profile.name || '',
        year: profile.year || '2nd Year',
        target_role: profile.target_role || '',
        daily_hours: profile.daily_hours || 4,
      });
      setStep('profile_form');
      return;
    }

    setLoading(true);
    setLoadingText("Checking skill database...");
    try {
      const dbCheck = await checkSkillExists(skill);
      if (dbCheck.exists) {
        setLoadingText("Generating...");
      } else {
        setLoadingText("Generating skill roadmap using AI...");
      }
      setProfileForm({
        name: profile.name || '',
        year: profile.year || '2nd Year',
        target_role: profile.target_role || '',
        daily_hours: profile.daily_hours || 4,
      });
      setStep('profile_form');
    } catch (err) {
      console.error(err);
      setLoadingText("Generating...");
      setProfileForm({
        name: profile.name || '',
        year: profile.year || '2nd Year',
        target_role: profile.target_role || '',
        daily_hours: profile.daily_hours || 4,
      });
      setStep('profile_form');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    setLoading(true);
    setError('');
    setData(null);
    setStep('loading');

    try {
      // Step 1: Save profile to Supabase
      const updatedProfile = await updateStudentProfile(1, profileForm);
      setProfile(updatedProfile);

      const skill = query.trim();

      // Step 2: Check Mock Data
      const matchKey = Object.keys(MOCK_SKILLS).find(
        k => k.toLowerCase() === skill.toLowerCase()
      );

      if (matchKey) {
        setTimeout(() => {
          setData({
            skill: MOCK_SKILLS[matchKey],
            student: updatedProfile,
            learningPlan: MOCK_LEARNING_PLANS[matchKey] || [],
            resources: MOCK_RESOURCES[matchKey] || [],
            projects: MOCK_PROJECTS[matchKey] || [],
            tips: MOCK_TIPS[matchKey] || [],
            is_fallback: false,
          });
          setStep('results');
          setLoading(false);
        }, 500); // Small artificial delay for mock
        return;
      }

      // Step 3: Call Backend
      const backendData = await generateSkillRoadmap(skill, 1);
      setData({
        skill: backendData.skill,
        student: backendData.student,
        learningPlan: backendData.learning_plan,
        resources: backendData.resources,
        projects: backendData.projects,
        tips: backendData.placement_tips,
        is_fallback: backendData.is_fallback,
      });
      setStep('results');
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Unable to generate roadmap right now. Please try again later.");
      }
      setStep('search');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sk-page">
      {/* ── Hero Banner ─── */}
      <div className="sk-hero">
        <div className="sk-hero-content">
          <div className="sk-hero-badge">
            <Brain size={14} /> AI-Powered Skill Agent
          </div>
          <h1 className="sk-hero-title">Skills Learning Agent</h1>
          <p className="sk-hero-subtitle">
            Generate personalized skill roadmaps, resources, projects, and placement guidance.
          </p>
          <SkillSearch
            query={query}
            onChange={setQuery}
            onSubmit={handleGenerate}
            loading={loading}
          />
        </div>
      </div>

      {/* ── Error State ─── */}
      {error && (
        <div className="sk-error">
          <AlertCircle size={20} className="sk-error-icon" />
          <div>
            <div className="sk-error-title">Skill not found</div>
            <div className="sk-error-text">{error}</div>
          </div>
        </div>
      )}

      {/* ── Loading State ─── */}
      {loading && (
        <div style={{ textAlign: 'center', marginBottom: 24, padding: '24px 0', animation: 'skFadeIn 0.3s ease' }}>
          <div className="spinner" style={{ margin: '0 auto 16px auto', width: 36, height: 36 }} />
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 24 }}>
            {loadingText}
          </div>
          <SkeletonLoader />
        </div>
      )}


      {/* ── Empty State ─── */}
      {step === 'search' && !loading && !data && !error && (
        <div className="sk-empty-state">
          <div className="sk-empty-icon">
            <BookOpen size={36} color="var(--text-muted)" opacity={0.5} />
          </div>
          <div className="sk-empty-title">Search a skill to get started</div>
          <div className="sk-empty-subtitle">
            Enter a skill like RAG, NLP, React, or Agentic AI to generate a personalized learning roadmap with resources, projects, and placement tips.
          </div>
        </div>
      )}

      {/* ── Learning Profile Form ─── */}
      {step === 'profile_form' && !loading && (
        <div className="sk-profile-form-container" style={{ animation: 'skFadeIn 0.3s ease' }}>
          <div className="sk-profile-form-card">
            <h2 className="sk-form-title">Personalize Your Learning Profile</h2>
            <p className="sk-form-subtitle">
              Tailor your study settings for <strong>{query}</strong> so Gemini can generate a personalized weekly roadmap.
            </p>
            
            <div className="sk-form-group">
              <label className="sk-form-label" htmlFor="profile-name">Name</label>
              <input
                id="profile-name"
                className="sk-form-input"
                type="text"
                value={profileForm.name}
                onChange={e => setProfileForm({ ...profileForm, name: e.target.value })}
                placeholder="Enter your name"
              />
            </div>

            <div className="sk-form-grid">
              <div className="sk-form-group">
                <label className="sk-form-label" htmlFor="profile-year">Year of Study</label>
                <select
                  id="profile-year"
                  className="sk-form-select"
                  value={profileForm.year}
                  onChange={e => setProfileForm({ ...profileForm, year: e.target.value })}
                >
                  <option value="1st Year">1st Year</option>
                  <option value="2nd Year">2nd Year</option>
                  <option value="3rd Year">3rd Year</option>
                  <option value="Final Year">Final Year</option>
                </select>
              </div>

              <div className="sk-form-group">
                <label className="sk-form-label" htmlFor="profile-hours">Daily Study Hours</label>
                <input
                  id="profile-hours"
                  className="sk-form-input"
                  type="number"
                  min="1"
                  max="24"
                  value={profileForm.daily_hours}
                  onChange={e => setProfileForm({ ...profileForm, daily_hours: parseInt(e.target.value) || 0 })}
                  placeholder="e.g. 4"
                />
              </div>
            </div>

            <div className="sk-form-group">
              <label className="sk-form-label" htmlFor="profile-role">Target Career Role</label>
              <input
                id="profile-role"
                className="sk-form-input"
                type="text"
                value={profileForm.target_role}
                onChange={e => setProfileForm({ ...profileForm, target_role: e.target.value })}
                placeholder="e.g. AI Engineer, Software Engineer"
              />
            </div>

            <div className="sk-form-actions">
              <button 
                className="sk-btn-secondary" 
                onClick={() => {
                  setStep('search');
                  setData(null);
                }}
              >
                Back
              </button>
              <button 
                id="profile-submit-btn"
                className="sk-btn-primary" 
                onClick={handleGenerateRoadmap}
                disabled={!profileForm.name.trim() || !profileForm.target_role.trim() || !profileForm.daily_hours}
              >
                Generate Personalized Roadmap
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Results ─── */}
      {!loading && data && step === 'results' && (
        <div style={{ animation: 'skFadeIn 0.4s ease' }}>
          
          {data.is_fallback && (
            <div className="sk-fallback-badge" id="fallback-roadmap-badge">
              <AlertCircle size={16} />
              <span>Showing fallback roadmap</span>
            </div>
          )}

          <div className="sk-results-actions" style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 20 }}>
            <button 
              className="sk-edit-profile-btn" 
              onClick={() => {
                setProfileForm({
                  name: profile.name,
                  year: profile.year,
                  target_role: profile.target_role,
                  daily_hours: profile.daily_hours,
                });
                setStep('profile_form');
              }}
            >
              Edit Profile & Regenerate
            </button>
          </div>

          {/* Student Profile + Skill Overview */}
          <div className="sk-grid-top">
            <StudentProfileCard student={data.student} />
            <SkillOverviewCard skill={data.skill} />
          </div>

          {/* Learning Roadmap */}
          <RoadmapTimeline learningPlan={data.learningPlan} />

          {/* Resources + Projects */}
          <div className="sk-grid-bottom">
            <ResourceCards resources={data.resources} />
            <ProjectCards projects={data.projects} />
          </div>

          {/* Placement Tips */}
          <PlacementTips tips={data.tips} />
        </div>
      )}
    </div>
  );
}
