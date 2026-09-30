import { useMemo, useState } from "react";

const STORAGE_KEY = "hng15-todo-stage1";
const CATEGORIES = ["Work", "Personal", "School", "Shopping", "Health", "Finance", "Other"];

const SAMPLE_TASKS = [
  {
    id: "sample-1",
    title: "Finish Stage 1 submission",
    description: "Verify the public deployment and submit the final link.",
    category: "Work",
    due_at: new Date(Date.now() + 86400000).toISOString(),
    completed: false,
  },
  {
    id: "sample-2",
    title: "Review project documentation",
    description: "Check the README and deployment notes before submission.",
    category: "School",
    due_at: new Date(Date.now() + 172800000).toISOString(),
    completed: false,
  },
  {
    id: "sample-3",
    title: "Clean up task list",
    description: "Archive anything that is no longer relevant.",
    category: "Personal",
    due_at: null,
    completed: true,
  },
  {
    id: "sample-4",
    title: "Plan next week's priorities",
    description: "Write down the three most important outcomes for next week.",
    category: "Work",
    due_at: new Date(Date.now() + 604800000).toISOString(),
    completed: false,
  },
];

function readTasks() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function writeTasks(tasks) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function newId() {
  return crypto.randomUUID ? crypto.randomUUID() : String(Date.now() + Math.random());
}

function toLocalDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}

function toUtcISOString(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function formatDue(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? null
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function Summary({ label, value, icon }) {
  return (
    <article className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <i className={"fa-solid " + icon} />
    </article>
  );
}

function TaskRow({ task, onComplete, onEdit, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({
    title: task.title,
    description: task.description || "",
    category: task.category || "",
    due_at: toLocalDateTime(task.due_at),
  });

  function save() {
    const title = draft.title.trim();
    if (!title) return;
    onEdit(task.id, {
      ...task,
      title,
      description: draft.description.trim(),
      category: draft.category.trim(),
      due_at: toUtcISOString(draft.due_at),
    });
    setEditing(false);
  }

  if (editing) {
    return (
      <article className="task-card editing">
        <input
          className="edit-title"
          aria-label="Task title"
          maxLength="255"
          value={draft.title}
          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
        />
        <textarea
          rows="3"
          maxLength="5000"
          aria-label="Task description"
          value={draft.description}
          onChange={(e) => setDraft({ ...draft, description: e.target.value })}
        />
        <div className="inline-edit-row">
          <select
            aria-label="Task category"
            value={draft.category}
            onChange={(e) => setDraft({ ...draft, category: e.target.value })}
          >
            <option value="">No category</option>
            {CATEGORIES.map((category) => <option key={category}>{category}</option>)}
          </select>
          <input
            type="datetime-local"
            aria-label="Task due date"
            value={draft.due_at}
            onChange={(e) => setDraft({ ...draft, due_at: e.target.value })}
          />
        </div>
        <div className="task-actions">
          <button className="secondary-button" type="button" onClick={() => setEditing(false)}>Cancel</button>
          <button className="primary-button" type="button" onClick={save}>Save</button>
        </div>
      </article>
    );
  }

  return (
    <article className="task-card">
      <button
        className={"check-button" + (task.completed ? " completed" : "")}
        type="button"
        onClick={() => onComplete(task.id, !task.completed)}
        aria-label={(task.completed ? "Reopen " : "Complete ") + task.title}
      >
        <i className={task.completed ? "fa-solid fa-circle-check" : "fa-regular fa-circle"} />
      </button>
      <div className={"task-content" + (task.completed ? " completed" : "")}>
        <h3>{task.title}</h3>
        {task.description && <p>{task.description}</p>}
        <div className="task-meta">
          {task.category && <span><i className="fa-solid fa-tag" /> {task.category}</span>}
          {formatDue(task.due_at) && <span><i className="fa-regular fa-calendar" /> {formatDue(task.due_at)}</span>}
        </div>
      </div>
      <div className="task-actions">
        <button className="icon-button" type="button" onClick={() => setEditing(true)} aria-label={"Edit " + task.title}>
          <i className="fa-solid fa-pen" />
        </button>
        <button className="icon-button danger" type="button" onClick={() => onDelete(task)} aria-label={"Delete " + task.title}>
          <i className="fa-solid fa-trash" />
        </button>
      </div>
    </article>
  );
}

function TaskModal({ onClose, onSubmit }) {
  const [form, setForm] = useState({ title: "", description: "", category: "", due_at: "" });
  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  function submit(event) {
    event.preventDefault();
    if (!form.title.trim()) return;
    onSubmit({
      id: newId(),
      title: form.title.trim(),
      description: form.description.trim(),
      category: form.category.trim(),
      due_at: toUtcISOString(form.due_at),
      completed: false,
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
        <div className="modal-actions">
          <button type="button" className="secondary-button" onClick={onClose}>Cancel</button>
          <button className="primary-button">Create task</button>
        </div>
      </form>
    </div>
  );
}

export default function Dashboard() {
  const [tasks, setTasks] = useState(readTasks);
  const [filters, setFilters] = useState({
    search: "", completed: "", category: "", sort: "created_at", order: "desc",
  });
  const [modalOpen, setModalOpen] = useState(false);
  const [toast, setToast] = useState(null);

  function persist(nextTasks) {
    setTasks(nextTasks);
    writeTasks(nextTasks);
  }

  function notify(message, type = "success") {
    setToast({ message, type });
    window.setTimeout(() => setToast(null), 3000);
  }

  function updateFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function loadSampleData() {
    persist(SAMPLE_TASKS.map((task) => ({ ...task })));
    notify("Sample data loaded.");
  }

  function clearTasks() {
    persist([]);
    notify("Task list cleared.");
  }

  function createTask(task) {
    persist([task, ...tasks]);
    setModalOpen(false);
    notify("Task created.");
  }

  function completeTask(id, completed) {
    persist(tasks.map((task) => task.id === id ? { ...task, completed } : task));
    notify(completed ? "Task completed." : "Task reopened.");
  }

  function updateTask(id, updated) {
    persist(tasks.map((task) => task.id === id ? updated : task));
    notify("Task updated.");
  }

  function deleteTask(task) {
    if (!window.confirm('Delete "' + task.title + '"?')) return;
    persist(tasks.filter((item) => item.id !== task.id));
    notify("Task deleted.");
  }

  const categories = useMemo(() => {
    return [...new Set(tasks.map((task) => task.category).filter(Boolean))].sort();
  }, [tasks]);

  const filteredTasks = useMemo(() => {
    const search = filters.search.trim().toLowerCase();
    const result = tasks.filter((task) => {
      const matchesSearch = !search || [task.title, task.description, task.category]
        .some((value) => value?.toLowerCase().includes(search));
      const matchesStatus = !filters.completed || String(task.completed) === filters.completed;
      const matchesCategory = !filters.category || task.category === filters.category;
      return matchesSearch && matchesStatus && matchesCategory;
    });

    result.sort((a, b) => {
      let comparison = 0;
      if (filters.sort === "title") comparison = a.title.localeCompare(b.title);
      if (filters.sort === "created_at") comparison = String(a.id).localeCompare(String(b.id));
      if (filters.sort === "due_at") comparison = (a.due_at || "9999").localeCompare(b.due_at || "9999");
      if (filters.order === "desc") comparison *= -1;
      return comparison;
    });
    return result;
  }, [tasks, filters]);

  const completedCount = tasks.filter((task) => task.completed).length;
  const pendingCount = tasks.length - completedCount;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand"><span className="brand-mark"><i className="fa-solid fa-check" /></span>Todo List</div>
        <div className="header-user">
          <div className="user-copy"><strong>Stage 1 Demo</strong><span>Local workspace</span></div>
          <button className="secondary-button logout-button" type="button" onClick={loadSampleData}>
            <i className="fa-solid fa-wand-magic-sparkles" /> Load sample data
          </button>
        </div>
      </header>

      <main className="dashboard">
        <div className="welcome">
          <span className="eyebrow">Public demo</span>
          <h1>Your tasks, without the ceremony.</h1>
          <p>Try every core todo feature directly in the browser. No account required.</p>
        </div>

        <section className="summary-grid" aria-label="Task summary">
          <Summary label="Total tasks" value={tasks.length} icon="fa-list-check" />
          <Summary label="Completed" value={completedCount} icon="fa-circle-check" />
          <Summary label="Pending" value={pendingCount} icon="fa-clock" />
        </section>

        <div className="section-heading">
          <h2>Your tasks</h2>
          <span>{filteredTasks.length} matching task{filteredTasks.length === 1 ? "" : "s"}</span>
        </div>

        <section className="task-controls" aria-label="Task controls">
          <div className="search-box">
            <i className="fa-solid fa-magnifying-glass" />
            <input aria-label="Search tasks" placeholder="Search tasks..." value={filters.search} onChange={(e) => updateFilter("search", e.target.value)} />
          </div>
          <select aria-label="Completion filter" value={filters.completed} onChange={(e) => updateFilter("completed", e.target.value)}>
            <option value="">All status</option><option value="false">Pending</option><option value="true">Completed</option>
          </select>
          <select aria-label="Category filter" value={filters.category} onChange={(e) => updateFilter("category", e.target.value)}>
            <option value="">All categories</option>{categories.map((category) => <option key={category}>{category}</option>)}
          </select>
          <select aria-label="Sort tasks" value={filters.sort} onChange={(e) => updateFilter("sort", e.target.value)}>
            <option value="created_at">Created</option><option value="title">Title</option><option value="due_at">Due date</option>
          </select>
          <select aria-label="Sort order" value={filters.order} onChange={(e) => updateFilter("order", e.target.value)}>
            <option value="desc">Descending</option><option value="asc">Ascending</option>
          </select>
          <button className="primary-button" type="button" onClick={() => setModalOpen(true)}>
            <i className="fa-solid fa-plus" /> New task
          </button>
        </section>

        {filteredTasks.length ? (
          <div className="task-list">
            {filteredTasks.map((task) => (
              <TaskRow key={task.id} task={task} onComplete={completeTask} onEdit={updateTask} onDelete={deleteTask} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <i className="fa-regular fa-clipboard" />
            <h3>No tasks found</h3>
            <p>Create a task or load the sample data to explore the app.</p>
            <button className="secondary-button" type="button" onClick={loadSampleData}>Load sample data</button>
          </div>
        )}

        <div className="pagination">
          <button className="secondary-button" type="button" onClick={clearTasks} disabled={!tasks.length}>Clear all data</button>
        </div>
      </main>

      {modalOpen && <TaskModal onClose={() => setModalOpen(false)} onSubmit={createTask} />}
      {toast && (
        <div className={"toast toast-" + toast.type} role="alert">
          <i className="fa-solid fa-circle-check" />{toast.message}
          <button type="button" aria-label="Close notification" onClick={() => setToast(null)}>×</button>
        </div>
      )}
    </div>
  );
}
