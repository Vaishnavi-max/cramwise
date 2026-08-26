import React, { useState } from "react";
import { createRoot } from "react-dom/client";

import {
  LayoutDashboard,
  BookOpen,
  BarChart3,
  UploadCloud,
  MessageCircle,
  ClipboardList,
  FileText,
  Moon,
  Sun,
  Search,
  Bell,
  ChevronRight,
  Flame,
  CheckCircle2,
  Clock3,
  Sparkles,
  ArrowUpRight,
  Menu,
  X,
  FileUp,
  Brain,
  Target,
  TrendingUp,
  Circle,
} from "lucide-react";

import "./styles.css";


// ============================================================
// FASTAPI CONNECTION
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";

async function checkBackendConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/`);

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error("FastAPI connection failed:", error);
    return false;
  }
}


// ============================================================
// TEMPORARY FRONTEND DATA
// ============================================================
//
// These will later be replaced by real API responses from:
// M2 → M3 → M5 → M6
//
// Keeping them here means the UI can be developed
// independently while we connect the backend properly.
// ============================================================

const subjects = [
  {
    code: "BCS 306",
    name: "Compiler Design",
    progress: 68,
    pyqs: 32,
    topics: 17,
    high: 5,
  },
  {
    code: "BCS 302",
    name: "Wireless Networks",
    progress: 42,
    pyqs: 28,
    topics: 21,
    high: 8,
  },
  {
    code: "BCS 304",
    name: "Cloud Computing",
    progress: 81,
    pyqs: 24,
    topics: 14,
    high: 3,
  },
];

const topics = [
  {
    name: "Bottom-Up Parsing",
    unit: "Unit 2",
    priority: "HIGH",
    pyqs: 8,
    marks: 35,
    progress: 0,
  },
  {
    name: "Canonical LR Parsing",
    unit: "Unit 2",
    priority: "HIGH",
    pyqs: 7,
    marks: 30,
    progress: 0,
  },
  {
    name: "Syntax Analysis",
    unit: "Unit 1",
    priority: "HIGH",
    pyqs: 6,
    marks: 27,
    progress: 100,
  },
  {
    name: "Code Optimization",
    unit: "Unit 4",
    priority: "MEDIUM",
    pyqs: 5,
    marks: 20,
    progress: 30,
  },
  {
    name: "Intermediate Code Generation",
    unit: "Unit 3",
    priority: "MEDIUM",
    pyqs: 4,
    marks: 17,
    progress: 0,
  },
];

const repeated = [
  {
    question:
      "Describe the design goals and issues in MAC protocol design for ad-hoc networks.",
    count: 5,
    marks: 10,
    unit: 1,
  },
  {
    question:
      "Explain the concept of heterogeneous mesh networks and their use cases in VANETS.",
    count: 4,
    marks: 10,
    unit: 3,
  },
  {
    question:
      "Why is energy efficiency critical in WSNs?",
    count: 4,
    marks: 10,
    unit: 4,
  },
];


// ============================================================
// APP
// ============================================================

function App() {
  const [dark, setDark] = useState(false);
  const [page, setPage] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [subject, setSubject] = useState("Compiler Design");

  const [selectedTopic, setSelectedTopic] = useState(null);

  const [backendConnected, setBackendConnected] = useState(false);


  // ----------------------------------------------------------
  // Check FastAPI when application starts
  // ----------------------------------------------------------

  React.useEffect(() => {
    checkBackendConnection().then(setBackendConnected);
  }, []);


  // ----------------------------------------------------------
  // Navigation
  // ----------------------------------------------------------

  const go = (next) => {
    setPage(next);
    setSidebarOpen(false);
  };


  return (
    <div className={`app ${dark ? "dark" : ""}`}>

      {/* ====================================================
          SIDEBAR
      ==================================================== */}

      <aside
        className={`sidebar ${sidebarOpen ? "open" : ""}`}
      >

        <div className="brand">

          <div className="brand-mark">
            <Brain size={21} />
          </div>

          <div>
            <div className="brand-name">
              CramWise
            </div>

            <div className="brand-sub">
              Study smarter.
            </div>
          </div>

          <button
            className="icon-btn mobile-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} />
          </button>

        </div>


        <div className="nav-label">
          Workspace
        </div>

        <nav>

          <NavItem
            icon={<LayoutDashboard size={18} />}
            label="Dashboard"
            active={page === "dashboard"}
            onClick={() => go("dashboard")}
          />

          <NavItem
            icon={<BookOpen size={18} />}
            label="My Subjects"
            active={page === "subjects"}
            onClick={() => go("subjects")}
          />

          <NavItem
            icon={<BarChart3 size={18} />}
            label="Analytics"
            active={page === "analytics"}
            onClick={() => go("analytics")}
          />

          <NavItem
            icon={<ClipboardList size={18} />}
            label="Study Plan"
            active={page === "plan"}
            onClick={() => go("plan")}
          />

          <NavItem
            icon={<FileText size={18} />}
            label="PYQ Explorer"
            active={page === "pyqs"}
            onClick={() => go("pyqs")}
          />

        </nav>


        <div className="nav-label upload-label">
          Knowledge
        </div>

        <nav>

          <NavItem
            icon={<UploadCloud size={18} />}
            label="Upload Content"
            active={page === "upload"}
            onClick={() => go("upload")}
          />

          <NavItem
            icon={<MessageCircle size={18} />}
            label="CramWise Chat"
            active={page === "chat"}
            onClick={() => go("chat")}
          />

        </nav>


        <div className="sidebar-bottom">

          <div className="exam-card">

            <div className="exam-icon">
              <Target size={17} />
            </div>

            <div>

              <div className="exam-title">
                Exam readiness
              </div>

              <div className="exam-progress">
                <span style={{ width: "72%" }} />
              </div>

              <div className="exam-meta">
                72% overall
              </div>

            </div>

          </div>


          <div className="profile">

            <div className="avatar">
              V
            </div>

            <div className="profile-copy">
              <b>Vaishnavi</b>
              <span>Student</span>
            </div>

            <button
              className="icon-btn"
              onClick={() => setDark(!dark)}
              title="Toggle theme"
            >
              {dark ? (
                <Sun size={17} />
              ) : (
                <Moon size={17} />
              )}
            </button>

          </div>

        </div>

      </aside>


      {sidebarOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}


      {/* ====================================================
          MAIN
      ==================================================== */}

      <main className="main">

        <header className="topbar">

          <button
            className="icon-btn menu-btn"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>


          <div className="breadcrumb">
            CramWise
            <span>/</span>
            {pageLabel(page)}
          </div>


          <div className="top-actions">

            <div className="search-box">

              <Search size={16} />

              <input
                placeholder="Search topics, PYQs..."
              />

            </div>


            <button className="icon-btn notification">
              <Bell size={18} />
              <i />
            </button>


            <button
              className="theme-switch"
              onClick={() => setDark(!dark)}
            >
              {dark ? (
                <Sun size={16} />
              ) : (
                <Moon size={16} />
              )}
            </button>

          </div>

        </header>


        {/* ==================================================
            BACKEND STATUS
        ================================================== */}

        <div
          className={`backend-status ${
            backendConnected
              ? "connected"
              : "disconnected"
          }`}
        >

          <span className="status-dot" />

          {backendConnected
            ? "FastAPI connected"
            : "FastAPI not connected"}

        </div>


        <div className="content">

          {page === "dashboard" && (
            <Dashboard
              go={go}
              setSubject={setSubject}
            />
          )}


          {page === "subjects" && (
            <Subjects
              subject={subject}
              setSubject={setSubject}
              go={go}
              setSelectedTopic={setSelectedTopic}
            />
          )}


          {page === "analytics" && (
            <Analytics
              subject={subject}
            />
          )}


          {page === "plan" && (
            <StudyPlan
              go={go}
              setSelectedTopic={setSelectedTopic}
            />
          )}


          {page === "pyqs" && (
            <PYQs />
          )}


          {page === "upload" && (
            <UploadContent />
          )}


          {page === "chat" && (
            <Chat
              go={go}
              setSelectedTopic={setSelectedTopic}
            />
          )}


          {selectedTopic && (
            <TopicDrawer
              topic={selectedTopic}
              onClose={() => setSelectedTopic(null)}
            />
          )}

        </div>

      </main>

    </div>
  );
}


// ============================================================
// PAGE LABEL
// ============================================================

function pageLabel(page) {

  return (
    {
      dashboard: "Dashboard",
      subjects: "My Subjects",
      analytics: "Analytics",
      plan: "Study Plan",
      pyqs: "PYQ Explorer",
      upload: "Upload Content",
      chat: "CramWise Chat",
    }[page] || "Dashboard"
  );
}


// ============================================================
// NAV ITEM
// ============================================================

function NavItem({
  icon,
  label,
  active,
  onClick,
}) {

  return (
    <button
      className={`nav-item ${
        active ? "active" : ""
      }`}
      onClick={onClick}
    >

      {icon}

      <span>
        {label}
      </span>

      {active && (
        <span className="nav-dot" />
      )}

    </button>
  );
}


// ============================================================
// DASHBOARD
// ============================================================

function Dashboard({
  go,
  setSubject,
}) {

  return (
    <>

      <section className="hero">

        <div>

          <div className="eyebrow">
            <Sparkles size={14} />
            Your academic command center
          </div>

          <h1>
            Good morning, Vaishnavi 👋
          </h1>

          <p>
            Know what matters, learn what repeats,
            and prepare with confidence.
          </p>

        </div>


        <button
          className="primary-btn"
          onClick={() => go("plan")}
        >
          <Target size={17} />
          View today's plan
        </button>

      </section>


      <div className="stat-grid">

        <Stat
          icon={<BookOpen />}
          label="Subjects"
          value="5"
          note="2 need attention"
        />

        <Stat
          icon={<Brain />}
          label="Topics"
          value="42"
          note="17 completed"
        />

        <Stat
          icon={<FileText />}
          label="PYQs analyzed"
          value="68"
          note="+12 this week"
        />

        <Stat
          icon={<TrendingUp />}
          label="Overall progress"
          value="72%"
          note="↑ 8% this month"
        />

      </div>


      <div className="section-head">

        <div>
          <h2>Your subjects</h2>
          <p>Pick up where you left off.</p>
        </div>

        <button
          className="text-btn"
          onClick={() => go("subjects")}
        >
          View all
          <ChevronRight size={15} />
        </button>

      </div>


      <div className="subject-grid">

        {subjects.map((s) => (

          <SubjectCard
            key={s.code}
            subject={s}
            onClick={() => {
              setSubject(s.name);
              go("subjects");
            }}
          />

        ))}

      </div>


      <div className="dashboard-grid">

        <section className="panel">

          <div className="section-head compact">

            <div>
              <h2>Priority topics</h2>
              <p>
                Based on PYQ frequency and marks.
              </p>
            </div>

            <button
              className="text-btn"
              onClick={() => go("analytics")}
            >
              Analytics
              <ArrowUpRight size={15} />
            </button>

          </div>


          <div className="topic-list">

            {topics
              .slice(0, 4)
              .map((t) => (
                <TopicRow
                  key={t.name}
                  topic={t}
                />
              ))}

          </div>

        </section>


        <section className="panel readiness">

          <div className="section-head compact">

            <div>
              <h2>Preparation snapshot</h2>
              <p>Where your effort is going.</p>
            </div>

          </div>


          <Ring
            value={72}
            label="Overall"
          />


          <div className="mini-metrics">

            <MiniMetric
              label="High priority done"
              value="64%"
            />

            <MiniMetric
              label="PYQs covered"
              value="54%"
            />

            <MiniMetric
              label="Units completed"
              value="9 / 15"
            />

          </div>

        </section>

      </div>


      <div className="section-head">

        <div>
          <h2>Frequently asked</h2>
          <p>
            Questions worth revising first.
          </p>
        </div>

        <button
          className="text-btn"
          onClick={() => go("pyqs")}
        >
          Explore PYQs
          <ChevronRight size={15} />
        </button>

      </div>


      <div className="pyq-grid">

        {repeated.map((q, i) => (
          <PYQCard
            key={i}
            q={q}
          />
        ))}

      </div>

    </>
  );
}


// ============================================================
// STAT
// ============================================================

function Stat({
  icon,
  label,
  value,
  note,
}) {

  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>

      <div>

        <span>{label}</span>

        <strong>{value}</strong>

        <small>{note}</small>

      </div>

    </div>
  );
}


// ============================================================
// SUBJECT CARD
// ============================================================

function SubjectCard({
  subject,
  onClick,
}) {

  return (
    <button
      className="subject-card"
      onClick={onClick}
    >

      <div className="subject-top">

        <div className="subject-badge">
          {subject.code.split(" ")[1]}
        </div>

        <span
          className={`priority-pill ${
            subject.progress < 50
              ? "warn"
              : ""
          }`}
        >
          {subject.progress < 50
            ? "Needs focus"
            : "On track"}
        </span>

      </div>


      <h3>
        {subject.name}
      </h3>

      <p>
        {subject.code}
      </p>


      <div className="progress-label">

        <span>Progress</span>

        <b>
          {subject.progress}%
        </b>

      </div>


      <div className="progress">

        <span
          style={{
            width: `${subject.progress}%`,
          }}
        />

      </div>


      <div className="subject-meta">

        <span>
          <FileText size={14} />
          {subject.pyqs} PYQs
        </span>

        <span>
          <BookOpen size={14} />
          {subject.topics} topics
        </span>

        <span>
          <Flame size={14} />
          {subject.high} high
        </span>

      </div>

    </button>
  );
}


// ============================================================
// TOPIC ROW
// ============================================================

function TopicRow({
  topic,
}) {

  return (
    <div className="topic-row">

      <div
        className={`priority-dot ${
          topic.priority.toLowerCase()
        }`}
      />

      <div className="topic-main">

        <b>
          {topic.name}
        </b>

        <span>
          {topic.unit} · {topic.pyqs} PYQs ·{" "}
          {topic.marks} marks
        </span>

      </div>

      <span
        className={`priority-text ${
          topic.priority.toLowerCase()
        }`}
      >
        {topic.priority}
      </span>

    </div>
  );
}


// ============================================================
// PYQ CARD
// ============================================================

function PYQCard({
  q,
}) {

  return (
    <div className="pyq-card">

      <div className="q-icon">
        <FileText size={15} />
      </div>

      <h3>
        {q.question}
      </h3>

      <div className="pyq-card-meta">

        <span>
          Unit {q.unit}
        </span>

        <span>
          {q.marks} marks
        </span>

        <span>
          {q.count}× asked
        </span>

      </div>

    </div>
  );
}


// ============================================================
// MINI METRIC
// ============================================================

function MiniMetric({
  label,
  value,
}) {

  return (
    <div>

      <span>
        {label}
      </span>

      <b>
        {value}
      </b>

    </div>
  );
}


// ============================================================
// RING
// ============================================================

function Ring({
  value,
  label,
}) {

  return (
    <div className="ring-wrap">

      <div
        className="ring"
        style={{
          "--value": `${value * 3.6}deg`,
        }}
      >

        <div>

          <strong>
            {value}%
          </strong>

          <span>
            {label}
          </span>

        </div>

      </div>

    </div>
  );
}


// ============================================================
// SUBJECTS
// ============================================================

function Subjects({
  subject,
  setSubject,
  go,
  setSelectedTopic,
}) {

  return (
    <>

      <section className="page-title">

        <div>

          <div className="eyebrow">
            Subject workspace
          </div>

          <h1>
            {subject}
          </h1>

          <p>
            BCS 306 · 17 topics · 32 PYQs analyzed
          </p>

        </div>


        <button
          className="primary-btn"
          onClick={() => go("chat")}
        >
          <MessageCircle size={17} />
          Ask CramWise
        </button>

      </section>


      <div className="tabs">

        <button className="tab active">
          Overview
        </button>

        <button
          className="tab"
          onClick={() => go("analytics")}
        >
          Analytics
        </button>

        <button
          className="tab"
          onClick={() => go("pyqs")}
        >
          PYQs
        </button>

        <button
          className="tab"
          onClick={() => go("plan")}
        >
          Study plan
        </button>

      </div>


      <div className="subject-overview">

        <section className="panel big-progress">

          <div className="section-head compact">

            <div>

              <h2>
                Preparation progress
              </h2>

              <p>
                You're 68% through this subject.
              </p>

            </div>

            <span className="score">
              68%
            </span>

          </div>


          <div className="progress large">

            <span
              style={{
                width: "68%",
              }}
            />

          </div>


          <div className="overview-stats">

            <MiniMetric
              label="Completed"
              value="17 topics"
            />

            <MiniMetric
              label="Remaining"
              value="8 topics"
            />

            <MiniMetric
              label="High priority"
              value="5 topics"
            />

            <MiniMetric
              label="PYQs"
              value="32 analyzed"
            />

          </div>

        </section>


        <section className="panel">

          <div className="section-head compact">

            <div>

              <h2>
                Unit heatmap
              </h2>

              <p>
                Priority by unit.
              </p>

            </div>

          </div>


          <UnitBar
            unit="Unit 1"
            value={62}
          />

          <UnitBar
            unit="Unit 2"
            value={94}
          />

          <UnitBar
            unit="Unit 3"
            value={71}
          />

          <UnitBar
            unit="Unit 4"
            value={48}
          />

        </section>

      </div>


      <div className="section-head">

        <div>

          <h2>
            Topics to study
          </h2>

          <p>
            Sorted by importance and PYQ recurrence.
          </p>

        </div>

        <button className="filter-btn">
          <Flame size={15} />
          High priority first
        </button>

      </div>


      <div className="topic-cards">

        {topics.map((t) => (

          <button
            className="topic-card"
            key={t.name}
            onClick={() =>
              setSelectedTopic(t)
            }
          >

            <div className="topic-card-top">

              <span
                className={`priority-pill ${
                  t.priority.toLowerCase()
                }`}
              >
                {t.priority}
              </span>

              <span>
                {t.unit}
              </span>

            </div>


            <h3>
              {t.name}
            </h3>


            <p>
              {t.pyqs} previous questions ·{" "}
              {t.marks} marks
            </p>


            <div className="topic-card-bottom">

              <span>

                {t.progress === 100 ? (
                  <>
                    <CheckCircle2 size={15} />
                    Completed
                  </>
                ) : (
                  <>
                    <Circle size={15} />
                    Not completed
                  </>
                )}

              </span>

              <ChevronRight size={17} />

            </div>

          </button>

        ))}

      </div>

    </>
  );
}


// ============================================================
// UNIT BAR
// ============================================================

function UnitBar({
  unit,
  value,
}) {

  return (
    <div className="unit-bar">

      <div>

        <span>
          {unit}
        </span>

        <b>
          {value >= 80
            ? "Very high"
            : value >= 60
            ? "High"
            : "Medium"}
        </b>

      </div>


      <div className="progress">

        <span
          style={{
            width: `${value}%`,
          }}
        />

      </div>

    </div>
  );
}


// ============================================================
// ANALYTICS
// ============================================================

function Analytics({
  subject,
}) {

  return (
    <>

      <section className="page-title">

        <div>

          <div className="eyebrow">

            <BarChart3 size={14} />

            Intelligence layer

          </div>

          <h1>
            {subject} analytics
          </h1>

          <p>
            Turn your PYQs into a focused
            preparation strategy.
          </p>

        </div>


        <div className="date-chip">
          Updated today
        </div>

      </section>


      <div className="analytics-grid">

        <section className="panel chart-panel">

          <div className="section-head compact">

            <div>

              <h2>
                Topic priority distribution
              </h2>

              <p>
                How your syllabus is weighted.
              </p>

            </div>

          </div>


          <div className="bars">

            <Bar
              label="High"
              value={48}
            />

            <Bar
              label="Medium"
              value={32}
            />

            <Bar
              label="Low"
              value={20}
            />

          </div>

        </section>


        <section className="panel">

          <div className="section-head compact">

            <div>

              <h2>
                PYQ frequency
              </h2>

              <p>
                Most repeated topics.
              </p>

            </div>

          </div>


          <div className="rank-list">

            {topics
              .slice(0, 5)
              .map((t, i) => (

                <div
                  className="rank"
                  key={t.name}
                >

                  <span>
                    {String(i + 1).padStart(
                      2,
                      "0"
                    )}
                  </span>

                  <div>

                    <b>
                      {t.name}
                    </b>

                    <small>
                      {t.unit}
                    </small>

                  </div>

                  <strong>
                    {t.pyqs}×
                  </strong>

                </div>

              ))}

          </div>

        </section>

      </div>


      <section className="panel">

        <div className="section-head compact">

          <div>

            <h2>
              Unit-wise importance
            </h2>

            <p>
              Prioritize the units with
              the highest expected exam value.
            </p>

          </div>

        </div>


        <div className="unit-grid">

          <UnitImportance
            unit="Unit 1"
            marks="20%"
            value={55}
          />

          <UnitImportance
            unit="Unit 2"
            marks="35%"
            value={92}
          />

          <UnitImportance
            unit="Unit 3"
            marks="25%"
            value={72}
          />

          <UnitImportance
            unit="Unit 4"
            marks="20%"
            value={51}
          />

        </div>

      </section>

    </>
  );
}


// ============================================================
// ANALYTICS BAR
// ============================================================

function Bar({
  label,
  value,
}) {

  return (
    <div className="bar-item">

      <div
        className="bar-value"
        style={{
          height: `${value}%`,
        }}
      >

        <span>
          {value}%
        </span>

      </div>

      <b>
        {label}
      </b>

    </div>
  );
}


// ============================================================
// UNIT IMPORTANCE
// ============================================================

function UnitImportance({
  unit,
  marks,
  value,
}) {

  return (
    <div className="unit-importance">

      <div className="unit-number">
        {unit.replace("Unit ", "0")}
      </div>

      <div>

        <b>
          {unit}
        </b>

        <span>
          {marks} expected marks
        </span>

        <div className="progress">

          <span
            style={{
              width: `${value}%`,
            }}
          />

        </div>

      </div>

      <ArrowUpRight size={17} />

    </div>
  );
}


// ============================================================
// STUDY PLAN
// ============================================================

function StudyPlan({
  go,
  setSelectedTopic,
}) {

  return (
    <>

      <section className="page-title">

        <div>

          <div className="eyebrow">

            <Target size={14} />

            Focus mode

          </div>

          <h1>
            Today's study plan
          </h1>

          <p>
            4 hours available · optimized around
            priority and remaining topics.
          </p>

        </div>


        <button className="secondary-btn">

          <Clock3 size={16} />

          Change time

        </button>

      </section>


      <div className="plan-summary">

        <div>
          <span>Available</span>
          <b>4h</b>
        </div>

        <div>
          <span>Planned</span>
          <b>3h 30m</b>
        </div>

        <div>
          <span>High priority</span>
          <b>2 / 3</b>
        </div>

        <div>
          <span>Remaining</span>
          <b>30m</b>
        </div>

      </div>


      <div className="timeline">

        <PlanItem
          time="09:00 – 10:30"
          title="Bottom-Up Parsing"
          meta="Unit 2 · High priority · 8 PYQs"
          why="Frequently asked and worth 35 marks across analyzed papers."
          onClick={() =>
            setSelectedTopic(topics[0])
          }
        />

        <PlanItem
          time="10:30 – 11:30"
          title="Canonical LR Parsing"
          meta="Unit 2 · High priority · 7 PYQs"
          why="Builds directly on the first topic and has repeated exam coverage."
          onClick={() =>
            setSelectedTopic(topics[1])
          }
        />

        <PlanItem
          time="11:30 – 12:30"
          title="Code Optimization"
          meta="Unit 4 · Medium priority · 5 PYQs"
          why="Good use of remaining time after high-priority topics."
          onClick={() =>
            setSelectedTopic(topics[3])
          }
        />

        <PlanItem
          time="12:30 – 01:00"
          title="Quick PYQ revision"
          meta="3 repeated questions"
          why="Consolidate today's concepts before stopping."
          onClick={() => go("pyqs")}
        />

      </div>

    </>
  );
}


// ============================================================
// PLAN ITEM
// ============================================================

function PlanItem({
  time,
  title,
  meta,
  why,
  onClick,
}) {

  return (
    <div className="plan-item">

      <div className="time">
        {time}
      </div>

      <div className="timeline-dot" />

      <div className="plan-card">

        <div>

          <span className="eyebrow">

            <Flame size={13} />

            Recommended

          </span>

          <h3>
            {title}
          </h3>

          <p>
            {meta}
          </p>

          <small>
            {why}
          </small>

        </div>


        <button
          className="primary-btn small"
          onClick={onClick}
        >

          Start

          <ChevronRight size={15} />

        </button>

      </div>

    </div>
  );
}


// ============================================================
// PYQ EXPLORER
// ============================================================

function PYQs() {

  return (
    <>

      <section className="page-title">

        <div>

          <div className="eyebrow">

            <FileText size={14} />

            Your question bank

          </div>

          <h1>
            PYQ Explorer
          </h1>

          <p>
            Search, filter and learn from
            your university's actual questions.
          </p>

        </div>

      </section>


      <div className="filter-row">

        <div className="search-box wide">

          <Search size={16} />

          <input
            placeholder="Search previous-year questions..."
          />

        </div>

        <button className="filter-btn">
          Subject ▾
        </button>

        <button className="filter-btn">
          Unit ▾
        </button>

        <button className="filter-btn">
          Exam type ▾
        </button>

        <button className="filter-btn">
          Marks ▾
        </button>

      </div>


      <section className="panel">

        <div className="section-head compact">

          <div>

            <h2>
              Frequently asked
            </h2>

            <p>
              Sorted by recurrence.
            </p>

          </div>

        </div>


        <div className="pyq-list">

          {repeated
            .concat(repeated)
            .map((q, i) => (

              <div
                className="pyq-list-item"
                key={i}
              >

                <div className="pyq-number">
                  Q{i + 1}
                </div>

                <div className="pyq-copy">

                  <b>
                    {q.question}
                  </b>

                  <span>
                    BCS 302 · Unit {q.unit} ·{" "}
                    {q.marks} marks · Asked{" "}
                    {q.count} times
                  </span>

                </div>

                <button className="icon-btn">

                  <ChevronRight size={17} />

                </button>

              </div>

            ))}

        </div>

      </section>

    </>
  );
}


// ============================================================
// UPLOAD CONTENT
// ============================================================

function UploadContent() {
  const [files, setFiles] = useState({
    syllabus: null,
    pyq: null,
    notes: null,
  });

  const [uploading, setUploading] = useState({
    syllabus: false,
    pyq: false,
    notes: false,
  });

  const [uploadStatus, setUploadStatus] = useState({
    syllabus: null,
    pyq: null,
    notes: null,
  });

  // Notes must be associated with a real subject/course.
  // These values are sent to FastAPI and used by the notes
  // upload service to organize the uploaded document.
  const [notesSubject, setNotesSubject] = useState("");
  const [notesCourseCode, setNotesCourseCode] = useState("");

  const choose = (type, file) => {
    setFiles((previous) => ({
      ...previous,
      [type]: file,
    }));

    setUploadStatus((previous) => ({
      ...previous,
      [type]: null,
    }));
  };

  const uploadFile = async (type) => {
    const file = files[type];

    if (!file) return;

    setUploading((previous) => ({
      ...previous,
      [type]: true,
    }));

    setUploadStatus((previous) => ({
      ...previous,
      [type]: null,
    }));

    try {
      const formData = new FormData();

      if (type === "notes") {
        const subject = notesSubject.trim();
        const courseCode = notesCourseCode.trim();

        if (!subject) {
          throw new Error("Please enter the subject name.");
        }

        if (!courseCode) {
          throw new Error("Please enter the course code.");
        }

        formData.append("files", file);
        formData.append("subject", subject);
        formData.append("course_code", courseCode);
      } else {
        formData.append("file", file);
      }

      const endpoint =
        type === "syllabus"
          ? `${API_BASE_URL}/upload/syllabus`
          : type === "pyq"
            ? `${API_BASE_URL}/upload/pyq`
            : `${API_BASE_URL}/api/notes/upload`;

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
          data?.message ||
          `Upload failed with status ${response.status}`
        );
      }

      setUploadStatus((previous) => ({
        ...previous,
        [type]: {
          success: true,
          message:
            data?.message ||
            data?.status ||
            "File uploaded successfully.",
        },
      }));
    } catch (error) {
      console.error(`${type} upload failed:`, error);

      setUploadStatus((previous) => ({
        ...previous,
        [type]: {
          success: false,
          message:
            error.message ||
            "Could not connect to the CramWise backend.",
        },
      }));
    } finally {
      setUploading((previous) => ({
        ...previous,
        [type]: false,
      }));
    }
  };

  return (
    <>
      <section className="page-title">
        <div>
          <div className="eyebrow">
            <UploadCloud size={14} />
            Build your knowledge base
          </div>

          <h1>Upload academic content</h1>

          <p>
            Keep each content type separate so
            CramWise can process it correctly.
          </p>
        </div>
      </section>

      <div className="upload-grid">
        <UploadCard
          icon={<BookOpen />}
          title="Syllabus"
          description="Upload your official syllabus PDF. Used to map subjects, units and topics."
          file={files.syllabus}
          uploading={uploading.syllabus}
          status={uploadStatus.syllabus}
          onFile={(file) => choose("syllabus", file)}
          onUpload={() => uploadFile("syllabus")}
        />

        <UploadCard
          icon={<FileText />}
          title="Previous Year Questions"
          description="Upload PYQ papers. CramWise extracts questions, marks, units and exam metadata."
          file={files.pyq}
          uploading={uploading.pyq}
          status={uploadStatus.pyq}
          onFile={(file) => choose("pyq", file)}
          onUpload={() => uploadFile("pyq")}
        />

        <UploadCard
          icon={<BookOpen />}
          title="Notes"
          description="Upload lecture notes or study material. These become searchable knowledge for explanations."
          file={files.notes}
          uploading={uploading.notes}
          status={uploadStatus.notes}
          onFile={(file) => choose("notes", file)}
          onUpload={() => uploadFile("notes")}
          subject={notesSubject}
          courseCode={notesCourseCode}
          onSubjectChange={setNotesSubject}
          onCourseCodeChange={setNotesCourseCode}
        />
      </div>

      <div className="upload-note">
        <Sparkles size={18} />

        <div>
          <b>Tip for better results</b>

          <p>
            Upload clean PDFs with clear text.
            You can add multiple PYQ and Notes
            files over time.
          </p>
        </div>
      </div>
    </>
  );
}


// ============================================================
// UPLOAD CARD
// ============================================================

function UploadCard({
  icon,
  title,
  description,
  file,
  uploading,
  status,
  onFile,
  onUpload,
  subject = "",
  courseCode = "",
  onSubjectChange,
  onCourseCodeChange,
}) {
  return (
    <div className="upload-card">
      <div className="upload-icon">
        {icon}
      </div>

      <h2>{title}</h2>

      <p>{description}</p>

      {title === "Notes" && (
        <div className="notes-meta-fields">
          <div className="field-group">
            <label htmlFor="notes-subject">
              Subject
            </label>

            <input
              id="notes-subject"
              type="text"
              placeholder="e.g. Human Computer Interaction"
              value={subject}
              onChange={(event) =>
                onSubjectChange?.(event.target.value)
              }
              disabled={uploading}
            />
          </div>

          <div className="field-group">
            <label htmlFor="notes-course-code">
              Course Code
            </label>

            <input
              id="notes-course-code"
              type="text"
              placeholder="e.g. HCI301"
              value={courseCode}
              onChange={(event) =>
                onCourseCodeChange?.(event.target.value)
              }
              disabled={uploading}
            />
          </div>
        </div>
      )}

      <label className="dropzone">
        <FileUp size={23} />

        <b>
          {file ? file.name : "Choose a PDF"}
        </b>

        <span>
          {file
            ? "Ready to upload"
            : "or drag and drop here"}
        </span>

        <input
          type="file"
          accept=".pdf,.txt,.md"
          onChange={(event) => {
            const selectedFile =
              event.target.files?.[0];

            if (selectedFile) {
              onFile(selectedFile);
            }
          }}
        />
      </label>

      {file && (
        <div className="file-ready">
          <CheckCircle2 size={15} />
          File selected

          <button
            type="button"
            onClick={() => onFile(null)}
            disabled={uploading}
          >
            Change
          </button>
        </div>
      )}

      <button
        type="button"
        className="primary-btn full"
        disabled={
          !file ||
          uploading ||
          (title === "Notes" &&
            (!subject.trim() || !courseCode.trim()))
        }
        onClick={onUpload}
      >
        <UploadCloud size={16} />

        {uploading
          ? "Uploading..."
          : file
            ? "Upload content"
            : "Select a file first"}
      </button>

      {status && (
        <div
          className={`upload-status ${
            status.success ? "success" : "error"
          }`}
        >
          {status.message}
        </div>
      )}
    </div>
  );
}


// ============================================================
// CHAT
// ============================================================

function Chat({
  go,
  setSelectedTopic,
}) {

  const [
    messages,
    setMessages,
  ] = useState([
    {
      role: "assistant",
      text:
        "Hi! I'm CramWise. Ask me to explain a topic, find repeated PYQs, or help you decide what to study next.",
    },
  ]);


  const [
    input,
    setInput,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(false);


  // ----------------------------------------------------------
  // Chat request
  // ----------------------------------------------------------
  //
  // IMPORTANT:
  // We are NOT guessing your M6.5 endpoint here.
  //
  // Once we inspect your FastAPI routers, this function
  // will call the exact endpoint.
  //
  // ----------------------------------------------------------

  const send = async () => {

    if (!input.trim() || loading) {
      return;
    }


    const question = input.trim();


    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: question,
      },
    ]);


    setInput("");
    setLoading(true);


    try {

      /*
       * BACKEND CONNECTION POINT
       *
       * Replace this with the exact endpoint
       * exposed by your FastAPI M6/chat router.
       *
       * Example only:
       *
       * const response = await fetch(
       *   `${API_BASE_URL}/api/chat`,
       *   {
       *     method: "POST",
       *     headers: {
       *       "Content-Type": "application/json",
       *     },
       *     body: JSON.stringify({
       *       message: question,
       *     }),
       *   }
       * );
       */


      // For now, do not pretend that the backend
      // returned an answer when we haven't verified
      // the actual endpoint.

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            "Your question reached the CramWise chat UI. The exact FastAPI chat endpoint still needs to be connected to the backend router.",
        },
      ]);

    } catch (error) {

      console.error(
        "Chat request failed:",
        error
      );


      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            "I couldn't connect to the CramWise backend. Please make sure FastAPI is running.",
        },
      ]);

    } finally {

      setLoading(false);

    }

  };


  return (
    <div className="chat-layout">

      <section className="chat-panel">

        <div className="chat-head">

          <div className="chat-avatar">
            <Brain size={19} />
          </div>

          <div>

            <b>
              CramWise Assistant
            </b>

            <span>
              Academic preparation mode
            </span>

          </div>

          <span className="online" />

        </div>


        <div className="messages">

          {messages.map(
            (message, index) => (

              <div
                className={`message ${
                  message.role
                }`}
                key={index}
              >

                <div className="message-bubble">
                  {message.text}
                </div>

              </div>

            )
          )}


          {loading && (

            <div className="message assistant">

              <div className="message-bubble">
                Thinking...
              </div>

            </div>

          )}

        </div>


        <div className="suggestions">

          <button
            onClick={() =>
              setInput(
                "Explain Bottom-Up Parsing"
              )
            }
          >
            Explain a topic
          </button>


          <button
            onClick={() =>
              setInput(
                "Show repeated PYQs from Unit 2"
              )
            }
          >
            Find repeated PYQs
          </button>


          <button
            onClick={() =>
              setInput(
                "What should I study today?"
              )
            }
          >
            Plan my study
          </button>

        </div>


        <div className="chat-input">

          <input
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={(event) => {

              if (
                event.key === "Enter"
              ) {
                send();
              }

            }}
            placeholder="Ask anything about your subjects..."
          />


          <button
            onClick={send}
            disabled={loading}
          >
            <ArrowUpRight size={18} />
          </button>

        </div>

      </section>


      <aside className="chat-side">

        <div className="panel">

          <h3>
            Quick actions
          </h3>


          <button
            onClick={() =>
              setSelectedTopic(topics[0])
            }
          >
            <Brain size={16} />
            Learn Bottom-Up Parsing
          </button>


          <button
            onClick={() => go("pyqs")}
          >
            <FileText size={16} />
            Browse PYQs
          </button>


          <button
            onClick={() => go("analytics")}
          >
            <BarChart3 size={16} />
            View analytics
          </button>

        </div>

      </aside>

    </div>
  );
}


// ============================================================
// TOPIC DRAWER
// ============================================================

function TopicDrawer({
  topic,
  onClose,
}) {

  return (
    <div
      className="drawer-overlay"
      onClick={onClose}
    >

      <aside
        className="topic-drawer"
        onClick={(event) =>
          event.stopPropagation()
        }
      >

        <button
          className="icon-btn drawer-close"
          onClick={onClose}
        >
          <X size={18} />
        </button>


        <span
          className={`priority-pill ${
            topic.priority.toLowerCase()
          }`}
        >
          {topic.priority} PRIORITY
        </span>


        <h2>
          {topic.name}
        </h2>


        <p className="drawer-sub">
          {topic.unit} · {topic.pyqs} PYQs ·{" "}
          {topic.marks} marks
        </p>


        <div className="drawer-section">

          <h4>
            Why this matters
          </h4>

          <p>
            This topic has strong
            previous-year coverage and
            should be understood before
            lower-priority topics.
          </p>

        </div>


        <div className="drawer-section">

          <h4>
            What you'll learn
          </h4>

          <ul>

            <li>
              Core concept and intuition
            </li>

            <li>
              Step-by-step working
            </li>

            <li>
              Simple worked example
            </li>

            <li>
              How it appears in actual PYQs
            </li>

          </ul>

        </div>


        <button className="primary-btn full">

          <Sparkles size={16} />

          Start learning

        </button>

      </aside>

    </div>
  );
}


// ============================================================
// ROOT
// ============================================================

function AppRoot() {
  return <App />;
}


createRoot(
  document.getElementById("root")
).render(
  <AppRoot />
);