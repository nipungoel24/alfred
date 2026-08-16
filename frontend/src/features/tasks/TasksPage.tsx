import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';
import { tasks as fetchTasks, toggleTask, deleteTask, Task } from '../../api/emails';

export function TasksPage() {
  const queryClient = useQueryClient();
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

  const parentRef = useRef<HTMLDivElement>(null);
  
  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  
  // Show pending tasks by default
  const displayTasks = pendingTasks;

  const rowVirtualizer = useVirtualizer({
    count: displayTasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120, // Estimated height
  });

  if (isLoading) return <div className="p-8 text-center text-muted">Loading tasks...</div>;

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1>Derived Tasks</h1>
        <div className="text-muted">
          {pendingTasks.length} pending, {completedTasks.length} completed
        </div>
      </div>

      {displayTasks.length === 0 ? (
        <div className="panel p-8 text-center text-muted">
          No pending tasks detected in your inbox.
        </div>
      ) : (
        <div ref={parentRef} className="flex-1 overflow-auto bg-[#1e1e1e] border border-[#2d2d30] rounded-lg">
          <div
            style={{
              height: `${rowVirtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const task = displayTasks[virtualRow.index];
              return (
                <div
                  key={virtualRow.index}
                  data-index={virtualRow.index}
                  ref={rowVirtualizer.measureElement}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                  className="p-5 border-b border-[#2d2d30] flex items-start gap-4 hover:bg-[#252526] transition-colors"
                >
                  <button
                    className="mt-1 w-6 h-6 rounded-full border-2 border-primary flex items-center justify-center flex-shrink-0 hover:bg-primary/20"
                    onClick={() => toggleMutation.mutate(task.id)}
                    disabled={toggleMutation.isPending}
                  >
                    {/* Empty circle since it's pending */}
                  </button>
                  <div className="flex-1">
                    <div className="text-lg font-medium mb-1">{task.title}</div>
                    {task.description && (
                      <div className="text-muted text-sm mb-2">{task.description}</div>
                    )}
                    <div className="flex items-center gap-3">
                      {task.due_at && (
                        <span className="text-xs px-2 py-1 bg-purple/10 text-purple rounded">Due: {task.due_at}</span>
                      )}
                      {task.priority && (
                        <span className={`text-xs px-2 py-1 bg-opacity-10 rounded ${
                          task.priority === 'urgent' ? 'bg-danger text-danger' :
                          task.priority === 'high' ? 'bg-warning text-warning' :
                          'bg-primary text-primary'
                        }`}>
                          {task.priority.toUpperCase()}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    className="text-muted hover:text-danger p-2"
                    onClick={() => deleteMutation.mutate(task.id)}
                    disabled={deleteMutation.isPending}
                    title="Delete task"
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
