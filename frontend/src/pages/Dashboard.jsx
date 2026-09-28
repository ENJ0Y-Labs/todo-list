import { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

const CATEGORIES = ["Work", "Personal", "School", "Shopping", "Health", "Finance", "Other"];
const DEFAULT_FILTERS = {
  search: "", completed: "", category: "", due_after: "", due_before: "",
  sort: "created_at", order: "desc", page: 1,
};

function messageFor(error) {
  const messages = {
    TASK_TITLE_ALREADY_EXISTS: "An active task with that title already exists.",
    RESOURCE_NOT_FOUND: "That task is no longer available.",
    AUTHENTICATION_REQUIRED: "Your session has expired. Please sign in again.",
    VALIDATION_ERROR: error?.message,
  };
  return messages[error?.code] || error?.message || "Something went wrong.";
}

function toLocalDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function formatDue(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Invalid due date"
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function Summary({ label, value, icon }) {
  return <article className="summary-card"><span>{label}</span><strong>{value}</strong><i className={"fa-solid " + icon} /></article>;
}

function TaskRow({ task, busy, onComplete, onEdit, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({
    title: task.title,
    description: task.description || "",
    category: task.category || "",
    customCategory: "",
    due_at: toLocalDateTime(task.due_at),
  });

  useEffect(() => {
    setDraft({
      title: task.title,
      description: task.description || "",
      category: task.category || "",
      customCategory: "",
      due_at: toLocalDateTime(task.due_at),
    });
  }, [task]);

  const knownCategory = CATEGORIES.includes(draft.category) ? draft.category : draft.category ? "Other" : "";

  async function save() {
    const category = knownCategory === "Other" ? draft.customCategory.trim() : draft.category.trim();
    await onEdit(task.id, {
      title: draft.title.trim(),
      description: draft.description.trim() || null,
      category: category || null,
      due_at: draft.due_at ? new Date(draft.due_at).toISOString() : null,
    });
    setEditing(false);
  }

  if (editing) {
    return (
      <article className="task-card editing">
        <input className="edit-title" aria-label="Task title" maxLength="255" value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} />
        <textarea rows="3" maxLength="5000" aria-label="Task description" value={draft.description} onChange={(e) => setDraft({ ...draft, description: e.target.value })} />
        <div className="inline-edit-row">
          <select aria-label="Task category" value={knownCategory} onChange={(e) => setDraft({ ...draft, category: e.target.value, customCategory: "" })}>
            <option value="">No category</option>
            {CATEGORIES.map((category) => <option key={category}>{category}</option>)}
          </select>
          <input type="datetime-local" aria-label="Task due date" value={draft.due_at} onChange={(e) => setDraft({ ...draft, due_at: e.target.value })} />
        </div>
        {knownCategory === "Other" && (
          <input maxLength="100" aria-label="Custom category" placeholder="Custom category" value={draft.customCategory} onChange={(e) => setDraft({ ...draft, customCategory: e.target.value })} />
        )}
        <div className="task-actions">
          <button className="secondary-button" type="button" onClick={() => setEditing(false)}>Cancel</button>
          <button className="primary-button" type="button" disabled={busy} onClick={save}>Save</button>
        </div>
      </article>
    );
  }

  return (
    <article className="task-card">
      <button className="check-button" type="button" disabled={busy} onClick={() => onComplete(task.id, true)} aria-label={"Complete " + task.title}>
        <i className="fa-regular fa-circle" />
      </button>
      <div className="task-content">
        <h3>{task.title}</h3>
        {task.description && <p>{task.description}</p>}
        <div className="task-meta">
          {task.category && <span><i className="fa-solid fa-tag" /> {task.category}</span>}
          {formatDue(task.due_at) && <span><i className="fa-regular fa-calendar" /> {formatDue(task.due_at)}</span>}
        </div>
      </div>
      <div className="task-actions">
        <button className="icon-button" type="button" disabled={busy} onClick={() => setEditing(true)} aria-label={"Edit " + task.title}><i className="fa-solid fa-pen" /></button>
        <button className="icon-button danger" type="button" disabled={busy} onClick={() => onDelete(task)} aria-label={"Delete " + task.title}><i className="fa-solid fa-trash" /></button>
      </div>
    </article>
  );
}

function TaskModal({ onClose, onSubmit, busy, error }) {
  const [form, setForm] = useState({ title: "", description: "", category: "", customCategory: "", due_at: "" });
  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  function submit(event) {
    event.preventDefault();
    const category = form.category === "Other" ? form.customCategory.trim() : form.category.trim();
    onSubmit({
      title: form.title.trim(),
      description: form.description.trim() || null,
      category: category || null,
      due_at: form.due_at ? new Date(form.due_at).toISOString() : null,
    });
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <form className="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-title" onSubmit={submit}>
        <div className="modal-heading">
          <div><span className="eyebrow">New task</span><h2 id="modal-title">Create task</h2></div>
          <button type="button" className="icon-button" aria-label="Close" onClick={onClose}>×</button>
        </div>
        <label>Title<input required maxLength="255" autoFocus value={form.title} onChange={(e) => update("title", e.target.value)} /></label>
        <label>Description<textarea rows="4" maxLength="5000" value={form.description} onChange={(e) => update("description", e.target.value)} /></label>
        <div className="form-row">
          <label>Category
            <select value={form.category} onChange={(e) => update("category", e.target.value)}>
              <option value="">No category</option>
              {CATEGORIES.map((category) => <option key={category}>{category}</option>)}
            </select>
          </label>
          <label>Due date and time<input type="datetime-local" value={form.due_at} onChange={(e) => update("due_at", e.target.value)} /></label>
        </div>
        {form.category === "Other" && <label>Custom category<input maxLength="100" value={form.customCategory} onChange={(e) => update("customCategory", e.target.value)} /></label>}
        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="modal-actions">
          <button type="button" className="secondary-button" onClick={onClose}>Cancel</button>
          <button className="primary-button" disabled={busy}>{busy ? "Creating..." : "Create task"}</button>
        </div>
      </form>
    </div>
  );
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, per_page: 20, total: 0, total_pages: 0 });
  const [summary, setSummary] = useState({ total: 0, completed: 0, pending: 0 });
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalBusy, setModalBusy] = useState(false);
  const [modalError, setModalError] = useState("");
  const [toast, setToast] = useState(null);

  const notify = useCallback((message, type = "error") => {
    setToast({ message, type });
    window.setTimeout(() => setToast(null), 3500);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(filters.page),
        per_page: "20",
        sort: filters.sort,
        order: filters.order,
      });
      ["search", "completed", "category", "due_after", "due_before"].forEach((key) => {
        if (filters[key]) params.set(key, filters[key]);
      });

      const [list, total, completed, pending] = await Promise.all([
        api.listTasks(params.toString()),
        api.listTasks("page=1&per_page=1"),
        api.listTasks("page=1&per_page=1&completed=true"),
        api.listTasks("page=1&per_page=1&completed=false"),
      ]);

      setTasks(list.tasks || []);
      setPagination(list.pagination);
      setSummary({
        total: total.pagination.total,
        completed: completed.pagination.total,
        pending: pending.pagination.total,
      });
    } catch (error) {
      notify(messageFor(error));
    } finally {
      setLoading(false);
    }
  }, [filters, notify]);

  useEffect(() => {
    const delay = filters.search ? 300 : 0;
    const timer = window.setTimeout(load, delay);
    return () => window.clearTimeout(timer);
  }, [load, filters.search]);

  const categories = useMemo(() => {
    const taskCategories = tasks.map((task) => task.category).filter(Boolean);
    return [...new Set([...CATEGORIES.filter((c) => c !== "Other"), ...taskCategories])].sort();
  }, [tasks]);

  function setFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value, page: key === "page" ? value : 1 }));
  }

  async function createTask(payload) {
    setModalBusy(true);
    setModalError("");
    try {
      await api.createTask(payload);
      setModalOpen(false);
      notify("Task created.", "success");
      await load();
    } catch (error) {
      setModalError(messageFor(error));
    } finally {
      setModalBusy(false);
    }
  }

  async function completeTask(id) {
    setBusyId(id);
    try {
      await api.setTaskCompleted(id, true);
      setTasks((current) => current.filter((task) => task.id !== id));
      setSummary((current) => ({ ...current, completed: current.completed + 1, pending: Math.max(0, current.pending - 1) }));
      notify("Task completed.", "success");
      await load();
    } catch (error) {
      notify(messageFor(error));
    } finally {
      setBusyId(null);
    }
  }

  async function updateTask(id, payload) {
    setBusyId(id);
    try {
      await api.updateTask(id, payload);
      notify("Task updated.", "success");
      await load();
    } catch (error) {
      notify(messageFor(error));
      throw error;
    } finally {
      setBusyId(null);
    }
  }

  async function deleteTask(task) {
    if (!window.confirm('Delete "' + task.title + '"?')) return;
    setBusyId(task.id);
    try {
      await api.deleteTask(task.id);
      notify("Task deleted.", "success");
      await load();
    } catch (error) {
      notify(messageFor(error));
    } finally {
      setBusyId(null);
    }
  }

  async function signOut() {
    try {
      await logout();
    } catch (error) {
      notify(messageFor(error));
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand"><span className="brand-mark"><i className="fa-solid fa-check" /></span>Todo List</div>
        <div className="header-user">
          <div className="user-copy"><strong>{user?.fullname || user?.username}</strong><span>@{user?.username}</span></div>
          <button className="secondary-button logout-button" type="button" onClick={signOut}><i className="fa-solid fa-right-from-bracket" /> Logout</button>
        </div>
      </header>

      <main className="dashboard">
        <div className="welcome">
          <span className="eyebrow">Dashboard</span>
          <h1>Good to see you, {user?.fullname?.split(" ")[0] || user?.username}.</h1>
          <p>Keep the important work visible and the chaos contained.</p>
        </div>

        <section className="summary-grid" aria-label="Task summary">
          <Summary label="Total tasks" value={summary.total} icon="fa-list-check" />
          <Summary label="Completed" value={summary.completed} icon="fa-circle-check" />
          <Summary label="Pending" value={summary.pending} icon="fa-clock" />
        </section>

        <div className="section-heading"><h2>Your tasks</h2><span>{pagination.total} matching task{pagination.total === 1 ? "" : "s"}</span></div>

        <section className="task-controls" aria-label="Task controls">
          <div className="search-box"><i className="fa-solid fa-magnifying-glass" /><input aria-label="Search tasks" placeholder="Search tasks..." value={filters.search} onChange={(e) => setFilter("search", e.target.value)} /></div>
          <select aria-label="Completion filter" value={filters.completed} onChange={(e) => setFilter("completed", e.target.value)}><option value="">All status</option><option value="false">Pending</option><option value="true">Completed</option></select>
          <select aria-label="Category filter" value={filters.category} onChange={(e) => setFilter("category", e.target.value)}><option value="">All categories</option>{categories.map((category) => <option key={category}>{category}</option>)}</select>
          <input type="datetime-local" aria-label="Due after" title="Due after" value={filters.due_after} onChange={(e) => setFilter("due_after", e.target.value)} />
          <input type="datetime-local" aria-label="Due before" title="Due before" value={filters.due_before} onChange={(e) => setFilter("due_before", e.target.value)} />
          <select aria-label="Sort tasks" value={filters.sort} onChange={(e) => setFilter("sort", e.target.value)}><option value="created_at">Created</option><option value="title">Title</option><option value="due_at">Due date</option><option value="updated_at">Updated</option></select>
          <select aria-label="Sort order" value={filters.order} onChange={(e) => setFilter("order", e.target.value)}><option value="desc">Descending</option><option value="asc">Ascending</option></select>
          <button className="primary-button" type="button" onClick={() => { setModalError(""); setModalOpen(true); }}><i className="fa-solid fa-plus" /> New task</button>
        </section>

        {loading ? (
          <div className="spinner-wrap"><span className="spinner" aria-label="Loading tasks" /></div>
        ) : tasks.length ? (
          <div className="task-list">{tasks.map((task) => <TaskRow key={task.id} task={task} busy={busyId === task.id} onComplete={completeTask} onEdit={updateTask} onDelete={deleteTask} />)}</div>
        ) : (
          <div className="empty-state"><i className="fa-regular fa-clipboard" /><h3>No tasks found</h3><p>Create a task or change your filters.</p></div>
        )}

        {!loading && pagination.total_pages > 1 && (
          <nav className="pagination" aria-label="Task pagination">
            <button className="secondary-button" disabled={pagination.page <= 1} onClick={() => setFilter("page", pagination.page - 1)}>Previous</button>
            <span>Page {pagination.page} of {pagination.total_pages}</span>
            <button className="secondary-button" disabled={pagination.page >= pagination.total_pages} onClick={() => setFilter("page", pagination.page + 1)}>Next</button>
          </nav>
        )}
      </main>

      {modalOpen && <TaskModal onClose={() => setModalOpen(false)} onSubmit={createTask} busy={modalBusy} error={modalError} />}
      {toast && <div className={"toast toast-" + toast.type} role="alert"><i className={"fa-solid " + (toast.type === "success" ? "fa-circle-check" : "fa-circle-exclamation")} />{toast.message}<button type="button" aria-label="Close notification" onClick={() => setToast(null)}>×</button></div>}
    </div>
  );
}
