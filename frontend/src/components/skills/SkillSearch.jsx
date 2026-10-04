import { Search, Sparkles } from 'lucide-react';

export default function SkillSearch({ query, onChange, onSubmit, loading }) {
  return (
    <div className="sk-search-section">
      <div className="sk-search-input-wrap">
        <Search size={18} className="sk-search-icon" />
        <input
          id="skill-search-input"
          className="sk-search-input"
          type="text"
          placeholder="Enter Skill (RAG, NLP, React, LangGraph, Agentic AI...)"
          value={query}
          onChange={e => onChange(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && onSubmit()}
        />
      </div>
      <button
        id="skill-generate-btn"
        className="sk-generate-btn"
        onClick={onSubmit}
        disabled={loading || !query.trim()}
      >
        {loading ? (
          <>
            <span className="spinner" style={{ width: 16, height: 16, margin: 0 }} />
            Generating...
          </>
        ) : (
          <>
            <Sparkles size={16} />
            Generate Roadmap
          </>
        )}
      </button>
    </div>
  );
}
