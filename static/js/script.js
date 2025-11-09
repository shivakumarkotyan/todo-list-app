// Set min datetime for due date input
document.addEventListener('DOMContentLoaded', function() {
    const now = new Date();
    const localDateTime = now.toISOString().slice(0, 16);
    document.getElementById('due_date').min = localDateTime;
    
    loadTasks();
    checkEmailStatus(); // Add email status check on page load
    
    // Form submission
    document.getElementById('taskForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addTask();
    });
});

function addTask() {
    const formData = new FormData(document.getElementById('taskForm'));
    
    fetch('/add_task', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('taskForm').reset();
            loadTasks();
            showAlert('Task added successfully!', 'success');
        } else {
            showAlert('Error: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        showAlert('Error adding task: ' + error, 'danger');
    });
}

function loadTasks() {
    fetch('/get_tasks')
        .then(response => response.json())
        .then(tasks => {
            const tasksList = document.getElementById('tasksList');
            const taskCount = document.getElementById('taskCount');
            
            taskCount.textContent = `${tasks.length} task${tasks.length !== 1 ? 's' : ''}`;
            
            if (tasks.length === 0) {
                tasksList.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No tasks yet. Add your first task above!</p>
                    </div>
                `;
                return;
            }
            
            tasksList.innerHTML = tasks.map(task => `
                <div class="task-item card mb-3 ${task.completed ? 'task-completed' : ''} ${task.is_overdue && !task.completed ? 'task-overdue' : ''}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h5 class="card-title ${task.completed ? 'task-title-completed' : ''}">
                                    ${task.title}
                                    ${task.email_reminder ? '<i class="fas fa-bell text-warning ms-2" title="Email reminders enabled"></i>' : ''}
                                </h5>
                                ${task.description ? `<p class="card-text">${task.description}</p>` : ''}
                                <div class="d-flex gap-2 align-items-center mt-2">
                                    <span class="due-date-badge badge ${task.is_overdue && !task.completed ? 'bg-danger' : 'bg-secondary'}">
                                        <i class="fas fa-clock me-1"></i>Due: ${task.due_date}
                                    </span>
                                    ${task.completed ? '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Completed</span>' : ''}
                                    ${task.is_overdue && !task.completed ? '<span class="badge bg-danger"><i class="fas fa-exclamation-triangle me-1"></i>Overdue</span>' : ''}
                                </div>
                            </div>
                            <div class="btn-group ms-3">
                                <button class="btn btn-sm ${task.completed ? 'btn-warning' : 'btn-success'}" onclick="toggleComplete(${task.id})" title="${task.completed ? 'Mark as incomplete' : 'Mark as complete'}">
                                    <i class="fas ${task.completed ? 'fa-undo' : 'fa-check'}"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})" title="Delete task">
                                    <i class="fas fa-trash"></i>
                                </button>
                                ${task.email_reminder ? `<button class="btn btn-sm btn-info" onclick="sendTestReminder(${task.id})" title="Send test reminder">
                                    <i class="fas fa-paper-plane"></i>
                                </button>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        });
}

function toggleComplete(taskId) {
    window.location.href = `/complete_task/${taskId}`;
}

function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        window.location.href = `/delete_task/${taskId}`;
    }
}

function sendTestReminder(taskId) {
    if (confirm('Send demo email reminder for this task?')) {
        fetch(`/send_reminder/${taskId}`)
            .then(response => response.json())
            .then(data => {
                showAlert(data.message, data.success ? 'success' : 'warning');
            })
            .catch(error => {
                showAlert('Error sending reminder: ' + error, 'danger');
            });
    }
}

// Enhanced email status display with colors
function checkEmailStatus() {
    fetch('/email_status')
        .then(response => response.json())
        .then(data => {
            const statusDiv = document.getElementById('emailStatus');
            if (statusDiv) {
                const emailConfigBadge = data.email_configured ? 
                    '<span class="badge badge-configured status-badge">Yes</span>' : 
                    '<span class="badge badge-not-configured status-badge">No</span>';
                
                statusDiv.innerHTML = `
                    <div class="status-header">
                        <i class="fas fa-info-circle me-2"></i>Email Configuration Status
                    </div>
                    
                    <div class="status-item mode status-update">
                        <strong>Mode:</strong> 
                        <span class="badge badge-mode status-badge">${data.mode || 'Demo Mode'}</span>
                    </div>
                    
                    <div class="status-item configured status-update">
                        <strong>Status:</strong> 
                        <span class="badge badge-configured status-badge">Configured</span>
                    </div>
                    
                    <div class="status-item email-status status-update">
                        <strong>Email Configured:</strong> 
                        ${emailConfigBadge}
                    </div>
                    
                    <div class="status-details">
                        <i class="fas fa-lightbulb me-2"></i>
                        All email functions are simulated in demo mode
                    </div>
                `;
            }
        })
        .catch(error => {
            const statusDiv = document.getElementById('emailStatus');
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Unable to check email status: ${error.message}
                    </div>
                `;
            }
        });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}
// Add these functions to your existing JavaScript

function testEmailConnection() {
    console.log('Testing email connection...');
    fetch('/test_email')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('✅ ' + data.message, 'success');
            } else {
                showAlert('❌ ' + data.message, 'warning');
            }
        })
        .catch(error => {
            showAlert('❌ Error testing email: ' + error, 'danger');
        });
}

function sendAllDemoReminders() {
    if (confirm('Send demo email reminders for all tasks with email notifications enabled?')) {
        console.log('Sending demo reminders...');
        fetch('/demo_send_all_reminders')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('✅ ' + data.message, 'success');
                } else {
                    showAlert('❌ ' + data.message, 'warning');
                }
            })
            .catch(error => {
                showAlert('❌ Error sending reminders: ' + error, 'danger');
            });
    }
}

// Email Writer System Functions
function checkEmailStatus() {
    fetch('/get_email_status')
        .then(response => response.json())
        .then(data => {
            const statusDiv = document.getElementById('emailStatus');
            if (statusDiv) {
                const status = data.status_details;
                statusDiv.innerHTML = `
                    <div class="alert alert-info">
                        <h6><i class="fas fa-info-circle me-2"></i>Email System Status</h6>
                        <hr>
                        <div class="row">
                            <div class="col-6">
                                <strong>System Status:</strong> 
                                <span class="badge bg-success">Active</span>
                            </div>
                            <div class="col-6">
                                <strong>Total Emails:</strong> ${status.total_emails}
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <strong>Successful:</strong> 
                                <span class="badge bg-success">${status.successful_emails}</span>
                            </div>
                            <div class="col-6">
                                <strong>Failed:</strong> 
                                <span class="badge bg-danger">${status.failed_emails}</span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                Last activity: ${status.last_activity}
                            </small>
                        </div>
                    </div>
                `;
                showAlert('✅ Email system status checked successfully!', 'success');
            }
        })
        .catch(error => {
            showAlert('❌ Error checking email status: ' + error, 'danger');
        });
}

function testEmailConnection() {
    fetch('/test_email_config')
        .then(response => response.json())
        .then(data => {
            showAlert(data.message, data.success ? 'success' : 'warning');
        })
        .catch(error => {
            showAlert('❌ Error testing email connection: ' + error, 'danger');
        });
}

function sendBulkReminders() {
    if (confirm('Send email reminders for all tasks with email notifications enabled?')) {
        fetch('/send_bulk_reminders')
            .then(response => response.json())
            .then(data => {
                showAlert(data.message, data.success ? 'success' : 'warning');
                loadTasks(); // Reload tasks to show updates
            })
            .catch(error => {
                showAlert('❌ Error sending reminders: ' + error, 'danger');
            });
    }
}

function showEmailHistory() {
    fetch('/get_email_history')
        .then(response => response.json())
        .then(data => {
            const historyDiv = document.getElementById('emailHistory');
            const contentDiv = document.getElementById('historyContent');
            
            if (data.history.length === 0) {
                contentDiv.innerHTML = '<p class="text-muted">No email history found.</p>';
            } else {
                contentDiv.innerHTML = data.history.map(item => `
                    <div class="border-bottom pb-2 mb-2">
                        <div class="d-flex justify-content-between">
                            <strong>${item.task_title || 'Test Email'}</strong>
                            <span class="badge ${item.status === 'sent' ? 'bg-success' : 'bg-danger'}">
                                ${item.status}
                            </span>
                        </div>
                        <small class="text-muted">
                            To: ${item.recipient_email} | 
                            ${item.timestamp}
                        </small>
                        ${item.user_message ? `<div><small>Message: ${item.user_message}</small></div>` : ''}
                    </div>
                `).join('');
            }
            
            historyDiv.style.display = 'block';
            showAlert('📊 Email history loaded successfully!', 'info');
        })
        .catch(error => {
            showAlert('❌ Error loading email history: ' + error, 'danger');
        });
}

// Enhanced sendTestReminder function with email input
function sendTestReminder(taskId) {
    const recipientEmail = prompt('Enter recipient email address:', 'tasker@example.com');
    const userMessage = prompt('Enter your message (optional):', 'Task reminder');
    
    if (recipientEmail) {
        fetch(`/send_task_email/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recipient_email: recipientEmail,
                message: userMessage || ''
            })
        })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message, data.success ? 'success' : 'warning');
        })
        .catch(error => {
            showAlert('❌ Error sending email: ' + error, 'danger');
        });
    }
}