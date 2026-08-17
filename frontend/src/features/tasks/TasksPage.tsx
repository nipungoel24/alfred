import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef, useState } from 'react';
import { tasks as fetchTasks, toggleTask, deleteTask } from '../../api/emails';
import { Check, Trash2, CheckSquare } from 'lucide-react';

export function TasksPage() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<'pending' | 'completed' | 'all'>('pending');

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
  });

  const toggleMutation = useMutation({
    mutationFn: toggleTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  });

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const displayTasks = filter === 'pending' ? pendingTasks : filter === 'completed' ? completedTasks : tasks;

  const parentRef = useRef<HTMLDivElement>(null);
  const rowVirtualizer = useVirtualizer({
    count: displayTasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 8,
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-head">
        <div>
          <h1 className="page-title">Tasks</h1>
          <div className="page-subtitle">{pendingTasks.length} pending · {completedTasks.length} completed</div>
        </div>
        <div style={{ display: 'flex', gap: 2, border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', background: 'var(--bg-input)' }}>
          {(['pending', 'completed', 'all'] as const).map(f => (
            <button
              key={f}
              type="button"
              className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilter(f)}
              aria-pressed={filter === f}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div style={{ padding: 'var(--space-4) var(--space-6)' }} aria-busy="true">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton-row">
              <div className="skeleton" style={{ width: '60%', height: 13 }} />
              <div className="skeleton" style={{ width: '30%', height: 11 }} />
            </div>
          ))}
        </div>
      ) : displayTasks.length === 0 ? (
        <div className="empty-state">
          <CheckSquare aria-hidden="true" />
          <p>{filter === 'pending' ? 'No pending tasks.' : filter === 'completed' ? 'No completed tasks.' : 'No tasks found.'}</p>
        </div>
      ) : (
        <div ref={parentRef} style={{ flex: 1, overflowY: 'auto', minHeight: 0, padding: 'var(--space-2) var(--space-6)' }}>
          <div style={{ height: rowVirtualizer.getTotalSize(), width: '100%', position: 'relative' }}>
            {rowVirtualizer.getVirtualItems().map(virtualRow => {
              const task = displayTasks[virtualRow.index];
              const isCompleted = task.status === 'completed';
              return (
                <div
                  key={task.id}
                  data-index={virtualRow.index}
                  ref={rowVirtualizer.measureElement}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  <div className="list-row" style={{ borderBottom: virtualRow.index === displayTasks.length - 1 ? 'none' : undefined }}>
                    <button
                      type="button"
                      className={`task-checkbox ${isCompleted ? 'checked' : ''}`}
                      onClick={() => toggleMutation.mutate(task.id)}
                      disabled={toggleMutation.isPending}
                      aria-label={isCompleted ? 'Mark incomplete' : 'Mark complete'}
                    >
                      {isCompleted && <Check aria-hidden="true" />}
                    </button>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div className={`task-title ${isCompleted ? 'completed' : ''}`}>{task.title}</div>
                      {task.description && (
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {task.description}
                        </div>
                      )}
                      <div className="task-meta">
                        {task.due_at && <span style={{ color: 'var(--accent-text)' }}>Due: {task.due_at}</span>}
                        {task.priority && <span className={`badge badge-${task.priority}`}>{task.priority}</span>}
                      </div>
                    </div>
                    <button
                      type="button"
                      className="icon-btn"
                      onClick={() => deleteMutation.mutate(task.id)}
                      disabled={deleteMutation.isPending}
                      aria-label="Delete task"
                    >
                      <Trash2 aria-hidden="true" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
