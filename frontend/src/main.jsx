import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");
const TASK_STATUSES = ["todo", "in_progress", "review", "blocked", "done"];
const TASK_PRIORITIES = ["low", "medium", "high", "urgent"];
const STATUS_LABELS = {
  todo: "To do",
  in_progress: "In progress",
  review: "Review",
  blocked: "Blocked",
  done: "Done",
};
const PRIORITY_LABELS = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

function getErrorMessage(error) {
  if (typeof error?.detail === "string") return error.detail;
  if (Array.isArray(error?.detail))
    return error.detail.map((item) => item.msg).join(", ");
  if (error?.message) return error.message;
  return "Something went wrong.";
}

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem("taskflow_access_token") || "",
  );
  const [refreshToken, setRefreshToken] = useState(
    () => localStorage.getItem("taskflow_refresh_token") || "",
  );
  const [user, setUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [tasks, setTasks] = useState([]);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [showAuth, setShowAuth] = useState(false);
  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    password: "",
  });
  const [projectForm, setProjectForm] = useState({ name: "", description: "" });
  const [taskForm, setTaskForm] = useState({
    title: "",
    description: "",
    priority: "medium",
    assigned_to_email: "",
    due_date: "",
  });

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId),
    [projects, selectedProjectId],
  );

  const completedTasks = tasks.filter((task) => task.status === "done").length;
  const openTasks = tasks.length - completedTasks;

  async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (!(options.body instanceof FormData) && options.body !== undefined) {
      headers.set("Content-Type", "application/json");
    }
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const response = await fetch(`${API_URL}${path}`, { ...options, headers });
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      throw data || new Error(`Request failed with status ${response.status}`);
    }

    return data;
  }

  async function loadMe() {
    if (!token) return;
    try {
      const profile = await request("/auth/v1/me");
      setUser(profile);
    } catch (error) {
      logout();
      setNotice(getErrorMessage(error));
    }
  }

  async function loadProjects() {
    if (!token) return;
    setLoading(true);
    try {
      const data = await request("/api/v1/projects?page=1&size=50");
      setProjects(data.items || []);
      if (!selectedProjectId && data.items?.length)
        setSelectedProjectId(data.items[0].id);
    } catch (error) {
      setNotice(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function loadTasks(projectId = selectedProjectId) {
    if (!token || !projectId) {
      setTasks([]);
      return;
    }
    try {
      setTasks(await request(`/api/v1/projects/${projectId}/tasks`));
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  useEffect(() => {
    if (token) {
      loadMe();
      loadProjects();
    }
  }, [token]);

  useEffect(() => {
    loadTasks(selectedProjectId);
  }, [selectedProjectId]);

  async function handleAuth(event) {
    event.preventDefault();
    setNotice("");
    setLoading(true);

    try {
      if (authMode === "signup") {
        await request("/auth/v1/signup", {
          method: "POST",
          body: JSON.stringify(authForm),
        });
        setNotice(
          "Account created. If email verification is enabled, verify your email before logging in.",
        );
        setAuthMode("login");
        return;
      }

      const formData = new FormData();
      formData.append("username", authForm.email);
      formData.append("password", authForm.password);
      const data = await request("/auth/v1/login", {
        method: "POST",
        body: formData,
      });
      setToken(data.access_token);
      setRefreshToken(data.refresh_token || "");
      localStorage.setItem("taskflow_access_token", data.access_token);
      if (data.refresh_token)
        localStorage.setItem("taskflow_refresh_token", data.refresh_token);
      setNotice("Logged in successfully.");
    } catch (error) {
      setNotice(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function createProject(event) {
    event.preventDefault();
    setNotice("");
    try {
      const project = await request("/api/v1/projects", {
        method: "POST",
        body: JSON.stringify(projectForm),
      });
      setProjectForm({ name: "", description: "" });
      setSelectedProjectId(project.id);
      await loadProjects();
      setNotice("Project created.");
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  async function deleteProject(projectId) {
    if (!confirm("Delete this project and its tasks?")) return;
    try {
      await request(`/api/v1/projects/${projectId}`, { method: "DELETE" });
      setSelectedProjectId("");
      await loadProjects();
      setTasks([]);
      setNotice("Project deleted.");
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  async function createTask(event) {
    event.preventDefault();
    if (!selectedProjectId)
      return setNotice("Create or select a project first.");

    const payload = {
      ...taskForm,
      description: taskForm.description || null,
      assigned_to_email: taskForm.assigned_to_email || null,
      due_date: taskForm.due_date || null,
    };

    try {
      await request(`/api/v1/projects/${selectedProjectId}/tasks`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setTaskForm({
        title: "",
        description: "",
        priority: "medium",
        assigned_to_email: "",
        due_date: "",
      });
      await loadTasks();
      setNotice("Task created.");
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  async function updateTask(taskId, patch) {
    try {
      await request(`/api/v1/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify(patch),
      });
      await loadTasks();
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  async function deleteTask(taskId) {
    try {
      await request(`/api/v1/tasks/${taskId}`, { method: "DELETE" });
      await loadTasks();
      setNotice("Task deleted.");
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken)
      return setNotice("No refresh token saved. Please login again.");
    try {
      const data = await request("/auth/v1/refresh", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      setToken(data.access_token);
      localStorage.setItem("taskflow_access_token", data.access_token);
      setNotice("Access token refreshed.");
    } catch (error) {
      setNotice(getErrorMessage(error));
    }
  }

  async function logout() {
    try {
      if (token) {
        await request("/auth/v1/logout", {
          method: "POST",
          body: JSON.stringify({ refresh_token: refreshToken || null }),
        });
      }
    } catch {
      // Local logout should still happen if the API token is already expired.
    }
    setToken("");
    setRefreshToken("");
    setUser(null);
    setProjects([]);
    setTasks([]);
    setSelectedProjectId("");
    localStorage.removeItem("taskflow_access_token");
    localStorage.removeItem("taskflow_refresh_token");
  }

  if (!token && !showAuth) {
    return (
      <main className="landing-page">
        <nav className="landing-nav">
          <div className="brand-mark">TaskFlow</div>
          <div className="nav-actions">
            <button
              className="secondary"
              onClick={() => {
                setAuthMode("login");
                setShowAuth(true);
              }}
            >
              Login
            </button>
            <button
              onClick={() => {
                setAuthMode("signup");
                setShowAuth(true);
              }}
            >
              Get started
            </button>
          </div>
        </nav>

        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Project management for focused teams</p>
            <h1>Plan projects, assign tasks, and keep work moving.</h1>
            <p className="hero-text">
              TaskFlow connects a FastAPI backend with a clean React interface
              for managing projects, tasks, priorities, deadlines, and team
              ownership in one place.
            </p>
            <div className="hero-actions">
              <button
                onClick={() => {
                  setAuthMode("signup");
                  setShowAuth(true);
                }}
              >
                Create free account
              </button>
              <button
                className="secondary"
                onClick={() => {
                  setAuthMode("login");
                  setShowAuth(true);
                }}
              >
                I already have an account
              </button>
            </div>
          </div>

          <div className="hero-card card">
            <div className="mini-window-bar">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <h2>Today’s sprint</h2>
            <article className="preview-task active-preview">
              <strong>Design dashboard layout</strong>
              <small>High priority • In progress</small>
            </article>
            <article className="preview-task">
              <strong>Review auth flow</strong>
              <small>Medium priority • Review</small>
            </article>
            <article className="preview-task">
              <strong>Prepare API release</strong>
              <small>Urgent • Blocked</small>
            </article>
          </div>
        </section>

        <section className="feature-grid">
          <article className="feature-card">
            <span>01</span>
            <h3>Projects</h3>
            <p>Create project spaces and keep related work organized.</p>
          </article>
          <article className="feature-card">
            <span>02</span>
            <h3>Tasks</h3>
            <p>Track priorities, due dates, statuses, and ownership.</p>
          </article>
          <article className="feature-card">
            <span>03</span>
            <h3>Secure access</h3>
            <p>JWT authentication, refresh tokens, logout, and role checks.</p>
          </article>
        </section>
      </main>
    );
  }

  if (!token) {
    return (
      <main className="auth-page">
        <section className="card auth-card">
          <button className="back-button" onClick={() => setShowAuth(false)}>
            ← Back to home
          </button>
          <p className="eyebrow">TaskFlow</p>
          <h1>
            {authMode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="muted">
            {authMode === "login"
              ? "Enter your email and password to continue."
              : "Create an account to start organizing your work."}
          </p>

          <form onSubmit={handleAuth} className="stack">
            {authMode === "signup" && (
              <label>
                Name
                <input
                  placeholder="Your full name"
                  value={authForm.name}
                  onChange={(event) =>
                    setAuthForm({ ...authForm, name: event.target.value })
                  }
                  required
                />
              </label>
            )}
            <label>
              Email
              <input
                type="email"
                placeholder="you@example.com"
                value={authForm.email}
                onChange={(event) =>
                  setAuthForm({ ...authForm, email: event.target.value })
                }
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                placeholder="At least 6 characters"
                value={authForm.password}
                onChange={(event) =>
                  setAuthForm({ ...authForm, password: event.target.value })
                }
                required
              />
            </label>
            <button disabled={loading}>
              {loading
                ? "Please wait..."
                : authMode === "login"
                  ? "Login"
                  : "Sign up"}
            </button>
          </form>

          <button
            className="link-button"
            onClick={() =>
              setAuthMode(authMode === "login" ? "signup" : "login")
            }
          >
            {authMode === "login"
              ? "Need an account? Sign up"
              : "Already have an account? Login"}
          </button>
          {notice && <p className="notice">{notice}</p>}
          <p className="api-url">API: {API_URL}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">TaskFlow</p>
          <h1>Your workspace</h1>
          {user && (
            <p className="muted">
              Welcome, {user.name}. Manage projects and keep tasks moving.
            </p>
          )}
        </div>
        <div className="topbar-actions">
          <button className="secondary" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      {notice && <p className="notice">{notice}</p>}

      <section className="grid">
        <aside className="card sidebar-card">
          <div className="card-heading">
            <div>
              <h2>Projects</h2>
              <p className="muted">Create a space for each goal or client.</p>
            </div>
          </div>
          <form onSubmit={createProject} className="stack">
            <label>
              Project name
              <input
                placeholder="Website redesign"
                value={projectForm.name}
                onChange={(event) =>
                  setProjectForm({ ...projectForm, name: event.target.value })
                }
                required
              />
            </label>
            <label>
              Short description
              <textarea
                placeholder="What is this project about?"
                value={projectForm.description}
                onChange={(event) =>
                  setProjectForm({
                    ...projectForm,
                    description: event.target.value,
                  })
                }
                required
              />
            </label>
            <button>Create project</button>
          </form>

          <div className="list-heading">
            <h3>Your projects</h3>
            <span>{projects.length}</span>
          </div>
          {loading ? <p className="muted">Loading...</p> : null}
          <div className="project-list">
            {!loading && projects.length === 0 && (
              <div className="empty-state compact">
                <strong>No projects yet</strong>
                <p>Create your first project above to begin.</p>
              </div>
            )}
            {projects.map((project) => (
              <button
                key={project.id}
                className={
                  project.id === selectedProjectId
                    ? "project active"
                    : "project"
                }
                onClick={() => setSelectedProjectId(project.id)}
              >
                <span>{project.name}</span>
                <small>{project.description}</small>
              </button>
            ))}
          </div>
        </aside>

        <section className="card main-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Tasks</p>
              <h2>
                {selectedProject
                  ? selectedProject.name
                  : "Choose or create a project"}
              </h2>
              {selectedProject ? (
                <p className="muted">{selectedProject.description}</p>
              ) : (
                <p className="muted">
                  Select a project on the left to add and track tasks.
                </p>
              )}
            </div>
            {selectedProject && (
              <button
                className="danger"
                onClick={() => deleteProject(selectedProject.id)}
              >
                Delete project
              </button>
            )}
          </div>

          {selectedProject && (
            <div className="task-summary">
              <div>
                <strong>{tasks.length}</strong>
                <span>Total tasks</span>
              </div>
              <div>
                <strong>{openTasks}</strong>
                <span>Open</span>
              </div>
              <div>
                <strong>{completedTasks}</strong>
                <span>Done</span>
              </div>
            </div>
          )}

          <form onSubmit={createTask} className="task-form">
            <input
              disabled={!selectedProject}
              placeholder="Task title"
              value={taskForm.title}
              onChange={(event) =>
                setTaskForm({ ...taskForm, title: event.target.value })
              }
              required
            />
            <input
              disabled={!selectedProject}
              placeholder="Notes or details"
              value={taskForm.description}
              onChange={(event) =>
                setTaskForm({ ...taskForm, description: event.target.value })
              }
            />
            <select
              disabled={!selectedProject}
              aria-label="Task priority"
              value={taskForm.priority}
              onChange={(event) =>
                setTaskForm({ ...taskForm, priority: event.target.value })
              }
            >
              {TASK_PRIORITIES.map((priority) => (
                <option key={priority} value={priority}>
                  {PRIORITY_LABELS[priority]}
                </option>
              ))}
            </select>
            <input
              disabled={!selectedProject}
              type="email"
              placeholder="Assignee email"
              value={taskForm.assigned_to_email}
              onChange={(event) =>
                setTaskForm({
                  ...taskForm,
                  assigned_to_email: event.target.value,
                })
              }
            />
            <input
              disabled={!selectedProject}
              type="date"
              aria-label="Due date"
              value={taskForm.due_date}
              onChange={(event) =>
                setTaskForm({ ...taskForm, due_date: event.target.value })
              }
            />
            <button disabled={!selectedProject}>Add task</button>
          </form>

          <div className="task-list">
            {!selectedProject && (
              <div className="empty-state">
                <strong>No project selected</strong>
                <p>
                  Create a project or select one from the sidebar to start
                  adding tasks.
                </p>
              </div>
            )}
            {selectedProject && tasks.length === 0 && (
              <div className="empty-state">
                <strong>No tasks yet</strong>
                <p>
                  Add the first task above. Keep titles short and use priority
                  to plan your day.
                </p>
              </div>
            )}
            {tasks.map((task) => (
              <article key={task.id} className="task-card">
                <div>
                  <h3>{task.title}</h3>
                  {task.description && <p>{task.description}</p>}
                  <div className="task-meta">
                    <span className={`pill priority-${task.priority}`}>
                      {PRIORITY_LABELS[task.priority] || task.priority}
                    </span>
                    {task.due_date && (
                      <span className="pill neutral">Due {task.due_date}</span>
                    )}
                  </div>
                </div>
                <div className="task-actions">
                  <select
                    aria-label={`Status for ${task.title}`}
                    value={task.status}
                    onChange={(event) =>
                      updateTask(task.id, { status: event.target.value })
                    }
                  >
                    {TASK_STATUSES.map((status) => (
                      <option key={status} value={status}>
                        {STATUS_LABELS[status]}
                      </option>
                    ))}
                  </select>
                  <button
                    className="danger"
                    onClick={() => deleteTask(task.id)}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
