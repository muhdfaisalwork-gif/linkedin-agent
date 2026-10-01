// LinkedIn Nexus Agent - Autonomous LinkedIn Studio Application Logic

let currentPostDraft = null;
let currentProfileDraft = null;
let performanceChartInstance = null;
let loadedStories = [];
let savedPostsCache = [];

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    loadAnalytics();
    loadStoryBank();
    loadVoiceProfile();
    loadSettings();
    loadSavedDrafts();
    initChart();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAddStoryModal();
    }
});

// TAB SWITCHING
function switchTab(tabId) {
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.sidebar-btn').forEach(el => {
        el.classList.remove('bg-dark-700/70', 'border', 'border-dark-600', 'text-slate-200');
        el.classList.add('text-slate-400');
    });

    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    if (targetTab) targetTab.classList.remove('hidden');
    if (targetBtn) {
        targetBtn.classList.add('bg-dark-700/70', 'border', 'border-dark-600', 'text-slate-200');
        targetBtn.classList.remove('text-slate-400');
    }

    lucide.createIcons();
    if (tabId === 'analytics') loadAnalytics();
    if (tabId === 'studio') loadSavedDrafts();
    if (tabId === 'brain') { loadStoryBank(); loadVoiceProfile(); loadReflections(); }
    if (tabId === 'settings') loadSettings();
    if (tabId === 'reach') loadScannedFeed();
    if (tabId === 'seo') { loadGitHubSEOAudit(); selectLaunchChannel('hacker_news'); }
}

// 1. ANALYTICS & REACH
async function loadAnalytics() {
    try {
        const res = await fetch('/api/analytics/overview');
        const data = await res.json();

        if (data.totals) {
            document.getElementById('stat-impressions').innerText = (data.totals.impressions || 18450).toLocaleString();
            document.getElementById('stat-likes').innerText = (data.totals.likes || 642).toLocaleString();
            document.getElementById('stat-comments').innerText = (data.totals.comments || 158).toLocaleString();
        }

        const heuristicsContainer = document.getElementById('heuristics-list');
        if (heuristicsContainer && data.top_formulas) {
            heuristicsContainer.innerHTML = data.top_formulas.map(f => `
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-dark-900/60 border border-dark-700/50 text-xs">
                    <div>
                        <div class="font-bold text-slate-200 flex items-center gap-1.5">
                            <span class="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-mono text-[10px]">${f.formula_code}</span>
                            ${f.formula_name}
                        </div>
                        <div class="text-[10px] text-slate-400 mt-0.5">Used ${f.usage_count}x • Avg Eng: ${f.avg_engagement_rate}%</div>
                    </div>
                    <div class="text-right">
                        <span class="text-xs font-mono font-bold text-emerald-400">${f.weight.toFixed(2)}x</span>
                        <div class="text-[9px] text-slate-400">multiplier</div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Error loading analytics:', e);
    }
}

function initChart() {
    const ctx = document.getElementById('performanceChart')?.getContext('2d');
    if (!ctx) return;

    performanceChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Post 1 (F10)', 'Post 2 (F1)', 'Post 3 (F7)', 'Post 4 (F17)', 'Post 5 (F7)', 'Post 6 (F19)'],
            datasets: [
                {
                    label: 'Impressions',
                    data: [1800, 2400, 4200, 3100, 5600, 4900],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Engagements',
                    data: [120, 180, 460, 310, 620, 540],
                    borderColor: '#10b981',
                    backgroundColor: 'transparent',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
                y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
            }
        }
    });
}

async function simulateMetrics() {
    const impressions = Math.floor(Math.random() * 3000) + 1500;
    const likes = Math.floor(impressions * 0.05);
    const comments = Math.floor(impressions * 0.02);

    try {
        await fetch('/api/analytics/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_id: 1,
                impressions,
                likes,
                comments,
                reposts: Math.floor(comments * 0.3),
                saves: Math.floor(likes * 0.25)
            })
        });
        loadAnalytics();
        alert(`Recorded feedback: ${impressions} views, ${likes} likes, ${comments} comments! Heuristics evolved.`);
    } catch (e) {
        alert('Simulation error: ' + e);
    }
}

// 2. CONTENT STUDIO
async function generatePost() {
    const topic = document.getElementById('post-topic').value.trim();
    if (!topic) {
        alert('Please enter a post topic or insight.');
        return;
    }

    const hook = document.getElementById('post-hook').value;
    const angle = document.getElementById('post-angle').value;
    const visualType = document.getElementById('post-visual-type').value;
    const length = document.getElementById('post-length').value;

    const btn = document.getElementById('btn-generate-post');
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating 82-Rule Post...`;
    btn.disabled = true;

    try {
        const res = await fetch('/api/posts/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic,
                hook_code: hook,
                founder_angle_code: angle,
                target_length: length,
                visual_type: visualType
            })
        });

        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        currentPostDraft = data;

        // Render preview with fold highlight
        renderPostPreview(data.content, data.image_url);
        renderAudit(data.audit);

    } catch (e) {
        alert('Generation failed: ' + e.message);
    } finally {
        btn.innerHTML = `<i data-lucide="wand-2" class="w-4 h-4"></i> Generate Post & Visual`;
        btn.disabled = false;
        lucide.createIcons();
    }
}

function renderPostPreview(content, imageUrl) {
    const previewEl = document.getElementById('preview-text');
    if (!previewEl) return;
    // Highlight first 210 chars (LinkedIn fold) safely with HTML escaping
    if (content.length > 210) {
        const fold = escapeHtml(content.substring(0, 210));
        const rest = escapeHtml(content.substring(210));
        previewEl.innerHTML = `<span class="bg-blue-500/10 text-slate-900 border-b border-blue-400 font-medium" title="Above-the-fold hook">${fold}</span><span class="text-blue-600 font-semibold cursor-pointer"> … see more</span>\n\n${rest}`;
    } else {
        previewEl.innerText = content;
    }

    const imgContainer = document.getElementById('preview-image-container');
    if (imageUrl) {
        imgContainer.innerHTML = `<img src="${imageUrl}" class="w-full h-auto max-h-[360px] object-cover rounded-xl" alt="Post visual">`;
    }
}

function renderAudit(audit) {
    if (!audit) return;
    document.getElementById('audit-score-badge').innerText = `${audit.score} / 100`;
    document.getElementById('audit-char-count').innerText = audit.char_count || 0;
    document.getElementById('audit-flesch').innerText = audit.flesch_score || 70;
    document.getElementById('audit-dashes').innerText = audit.em_dash_count || 0;

    const violationsEl = document.getElementById('audit-violations');
    if (audit.violations && audit.violations.length > 0) {
        violationsEl.innerHTML = audit.violations.map(v => `
            <div class="text-rose-400 flex items-start gap-1.5">
                <i data-lucide="alert-triangle" class="w-3.5 h-3.5 mt-0.5 shrink-0"></i>
                <span><strong>${v.rule}:</strong> ${v.issue}</span>
            </div>
        `).join('');
    } else {
        violationsEl.innerHTML = `
            <div class="text-emerald-400 flex items-center gap-1.5">
                <i data-lucide="check" class="w-3.5 h-3.5"></i> 0 AI buzzwords. 82-Rule compliant human prose.
            </div>
        `;
    }
    lucide.createIcons();
}

async function humanizeEditor() {
    const topicText = document.getElementById('post-topic')?.value?.trim();
    const textToClean = (currentPostDraft && currentPostDraft.content) ? currentPostDraft.content : topicText;
    if (!textToClean) {
        alert('Please enter text in Post Topic or generate a draft first.');
        return;
    }
    try {
        const res = await fetch('/api/posts/humanize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textToClean })
        });
        const data = await res.json();
        if (currentPostDraft) {
            currentPostDraft.content = data.humanized_text;
            renderPostPreview(data.humanized_text, currentPostDraft.image_url);
        } else {
            document.getElementById('post-topic').value = data.humanized_text;
            renderPostPreview(data.humanized_text, null);
        }
        renderAudit(data.audit);
        alert('Humanizer 4-pass scrub complete!');
    } catch (e) {
        alert('Humanize error: ' + e);
    }
}

async function saveDraft() {
    if (!currentPostDraft) return;
    try {
        const res = await fetch('/api/posts/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_id: currentPostDraft.id || currentPostDraft.post_id,
                topic: currentPostDraft.topic,
                hook_formula: currentPostDraft.hook_formula,
                content: currentPostDraft.content,
                image_url: currentPostDraft.image_url,
                image_type: currentPostDraft.image_type,
                status: 'draft',
                flesch_score: currentPostDraft.audit?.flesch_score || 70,
                ai_tell_count: currentPostDraft.audit?.violations?.length || 0
            })
        });
        const saved = await res.json();
        if (saved.post_id) {
            currentPostDraft.id = saved.post_id;
            currentPostDraft.post_id = saved.post_id;
        }
        await loadSavedDrafts();
        alert('Post draft saved successfully!');
    } catch (e) {
        alert('Save error: ' + e);
    }
}

async function publishCurrentPost() {
    if (!currentPostDraft) {
        alert('Generate a post draft first.');
        return;
    }

    navigator.clipboard.writeText(currentPostDraft.content);

    // Save with status draft first, then publish endpoint updates status if dispatch succeeds
    try {
        const saveRes = await fetch('/api/posts/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_id: currentPostDraft.id || currentPostDraft.post_id,
                topic: currentPostDraft.topic,
                hook_formula: currentPostDraft.hook_formula,
                content: currentPostDraft.content,
                image_url: currentPostDraft.image_url,
                image_type: currentPostDraft.image_type,
                status: 'draft'
            })
        });
        const saved = await saveRes.json();
        const pubRes = await fetch(`/api/posts/publish/${saved.post_id}`, { method: 'POST' });
        const pubData = await pubRes.json();

        await loadSavedDrafts();
        alert(`✅ Post text copied to clipboard!\nStatus: ${pubData.dispatch_result?.status || pubData.status || 'published'}\n${pubData.dispatch_result?.message || ''}`);
        if (pubData.dispatch_result?.linkedin_composer_url) {
            window.open(pubData.dispatch_result.linkedin_composer_url, '_blank');
        }
    } catch (e) {
        alert('Publish error: ' + e);
    }
}

async function scheduleCurrentPost() {
    if (!currentPostDraft) {
        alert('Generate a post draft first.');
        return;
    }
    const scheduleInput = document.getElementById('post-schedule-time')?.value;
    if (!scheduleInput) {
        alert('Please select a date and time to schedule this post.');
        return;
    }

    try {
        const res = await fetch('/api/posts/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_id: currentPostDraft.id || currentPostDraft.post_id,
                topic: currentPostDraft.topic,
                hook_formula: currentPostDraft.hook_formula,
                content: currentPostDraft.content,
                image_url: currentPostDraft.image_url,
                image_type: currentPostDraft.image_type,
                status: 'scheduled',
                scheduled_time: scheduleInput
            })
        });
        const saved = await res.json();
        if (saved.post_id) {
            currentPostDraft.id = saved.post_id;
            currentPostDraft.post_id = saved.post_id;
        }
        await loadSavedDrafts();
        alert(`📅 Post scheduled for ${scheduleInput.replace('T', ' ')}!\nThe autonomous background agent will publish it automatically when due.`);
    } catch (e) {
        alert('Scheduling error: ' + e);
    }
}

// 2b. SAVED DRAFTS & POST HISTORY
async function loadSavedDrafts() {
    const list = document.getElementById('saved-drafts-list');
    if (!list) return;

    try {
        const res = await fetch('/api/posts');
        const posts = await res.json();
        savedPostsCache = posts;

        if (!posts || posts.length === 0) {
            list.innerHTML = `<div class="text-xs text-slate-500 py-2 text-center">No saved drafts found yet. Draft your first post above.</div>`;
            return;
        }

        list.innerHTML = posts.map(p => {
            const statusBadge = p.status === 'published'
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400">PUBLISHED</span>`
                : (p.status === 'scheduled'
                    ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/20 text-indigo-400">SCHEDULED</span>`
                    : `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-400">DRAFT</span>`);

            return `
                <div class="p-3 bg-dark-900 rounded-xl border border-dark-700/60 flex items-center justify-between gap-3 text-xs">
                    <div class="space-y-0.5 flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                            ${statusBadge}
                            <span class="font-bold text-slate-200 truncate">${escapeHtml(p.topic || 'Untitled Post')}</span>
                        </div>
                        <div class="text-[11px] text-slate-400 truncate">${escapeHtml(p.hook_formula || 'Standard')} • ${p.content ? p.content.length : 0} chars</div>
                    </div>
                    <div class="flex items-center gap-1.5 shrink-0">
                        <button onclick="loadDraftIntoStudio(${p.id})" class="px-2.5 py-1 bg-dark-700 hover:bg-dark-600 text-blue-400 rounded-lg text-xs font-medium transition flex items-center gap-1">
                            <i data-lucide="folder-open" class="w-3.5 h-3.5"></i> Load
                        </button>
                        <button onclick="deleteSavedDraft(${p.id})" class="p-1 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-dark-800 transition">
                            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        lucide.createIcons();
    } catch (e) {
        console.error('Error loading saved drafts:', e);
    }
}

function loadDraftIntoStudio(postId) {
    const post = savedPostsCache.find(p => p.id === postId);
    if (!post) return;

    currentPostDraft = post;
    document.getElementById('post-topic').value = post.topic || '';
    const hookSelect = document.getElementById('post-hook');
    if (hookSelect && post.hook_formula) {
        const code = post.hook_formula.split(' ')[0].trim();
        for (let i = 0; i < hookSelect.options.length; i++) {
            if (hookSelect.options[i].value === code) {
                hookSelect.selectedIndex = i;
                break;
            }
        }
    }
    renderPostPreview(post.content, post.image_url);
    if (post.flesch_score) {
        document.getElementById('audit-flesch').innerText = post.flesch_score;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function deleteSavedDraft(postId) {
    if (!confirm('Permanently delete this saved post?')) return;
    try {
        await fetch(`/api/posts/${postId}`, { method: 'DELETE' });
        if (currentPostDraft && (currentPostDraft.id === postId || currentPostDraft.post_id === postId)) {
            currentPostDraft = null;
        }
        await loadSavedDrafts();
    } catch (e) {
        alert('Delete post error: ' + e);
    }
}

// 3. COGNITIVE BRAIN & STORY BANK
async function loadStoryBank() {
    try {
        const res = await fetch('/api/brain/story-bank');
        loadedStories = await res.json();

        const countEl = document.getElementById('sidebar-receipts-count');
        if (countEl) countEl.innerText = loadedStories.length;

        const table = document.getElementById('story-bank-table');
        if (table) {
            table.innerHTML = loadedStories.map(s => `
                <div class="p-3.5 rounded-xl bg-dark-900 border border-dark-700/60 flex items-start justify-between gap-4">
                    <div class="space-y-1 flex-1">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-mono text-[10px]">${escapeHtml(s.category)}</span>
                            <span class="font-bold text-sm text-slate-100">${escapeHtml(s.title)}</span>
                            <span class="text-xs text-slate-400">(${escapeHtml(s.year_or_date) || '2025-2026'})</span>
                        </div>
                        <p class="text-xs text-slate-300">${escapeHtml(s.detail)}</p>
                        ${s.metrics_receipts ? `<div class="text-[11px] text-emerald-400 font-mono">📊 ${escapeHtml(s.metrics_receipts)}</div>` : ''}
                        ${s.url ? `<a href="${escapeHtml(s.url)}" target="_blank" class="text-[11px] text-blue-400 hover:underline flex items-center gap-1">🔗 ${escapeHtml(s.url)}</a>` : ''}
                    </div>
                    <div class="flex items-center gap-1">
                        <button onclick="openEditStoryModal(${s.id})" title="Edit Receipt" class="text-slate-400 hover:text-blue-400 p-1.5 rounded-lg hover:bg-dark-800 transition">
                            <i data-lucide="edit-3" class="w-4 h-4"></i>
                        </button>
                        <button onclick="deleteStory(${s.id})" title="Remove Receipt" class="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-dark-800 transition">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
            `).join('');
            lucide.createIcons();
        }
    } catch (e) {
        console.error('Error loading story bank:', e);
    }
}

function openAddStoryModal() {
    document.getElementById('modal-story-id').value = '';
    document.getElementById('modal-story-title').innerHTML = '<i data-lucide="plus-circle" class="w-5 h-5 text-blue-400"></i> Add Story Bank Receipt';
    document.getElementById('btn-submit-story').innerText = 'Save to Brain';
    document.getElementById('modal-category').value = '';
    document.getElementById('modal-title').value = '';
    document.getElementById('modal-detail').value = '';
    document.getElementById('modal-metrics').value = '';
    document.getElementById('modal-url').value = '';
    document.getElementById('modal-date').value = '';
    document.getElementById('modal-add-story').classList.remove('hidden');
    lucide.createIcons();
}

function openEditStoryModal(storyId) {
    const s = loadedStories.find(item => item.id === storyId);
    if (!s) return;
    document.getElementById('modal-story-id').value = s.id;
    document.getElementById('modal-story-title').innerHTML = '<i data-lucide="edit-3" class="w-5 h-5 text-amber-400"></i> Edit Story Bank Receipt';
    document.getElementById('btn-submit-story').innerText = 'Update in Brain';
    document.getElementById('modal-category').value = s.category || '';
    document.getElementById('modal-title').value = s.title || '';
    document.getElementById('modal-detail').value = s.detail || '';
    document.getElementById('modal-metrics').value = s.metrics_receipts || '';
    document.getElementById('modal-url').value = s.url || '';
    document.getElementById('modal-date').value = s.year_or_date || '';
    document.getElementById('modal-add-story').classList.remove('hidden');
    lucide.createIcons();
}

function closeAddStoryModal() {
    document.getElementById('modal-add-story').classList.add('hidden');
}

async function submitNewStory() {
    const storyId = document.getElementById('modal-story-id').value;
    const category = document.getElementById('modal-category').value.trim() || 'Product';
    const title = document.getElementById('modal-title').value.trim();
    const detail = document.getElementById('modal-detail').value.trim();
    const metrics = document.getElementById('modal-metrics').value.trim();
    const url = document.getElementById('modal-url').value.trim();
    const date = document.getElementById('modal-date').value.trim();

    if (!title || !detail) {
        alert('Please enter at least Title and Detail.');
        return;
    }

    try {
        if (storyId) {
            await fetch(`/api/brain/story-bank/${storyId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, title, detail, metrics, url, year_or_date: date })
            });
        } else {
            await fetch('/api/brain/story-bank', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, title, detail, metrics, url, year_or_date: date })
            });
        }
        closeAddStoryModal();
        loadStoryBank();
    } catch (e) {
        alert('Save error: ' + e);
    }
}

async function deleteStory(id) {
    if (!confirm('Remove this receipt from Brain?')) return;
    await fetch(`/api/brain/story-bank/${id}`, { method: 'DELETE' });
    loadStoryBank();
}

async function loadVoiceProfile() {
    try {
        const res = await fetch('/api/brain/voice-profile');
        const vp = await res.json();
        if (document.getElementById('voice-bio')) document.getElementById('voice-bio').value = vp.author_bio || '';
        if (document.getElementById('voice-preferred')) document.getElementById('voice-preferred').value = vp.preferred_phrases || '';
        if (document.getElementById('voice-banned')) document.getElementById('voice-banned').value = vp.banned_phrases || '';
    } catch (e) {
        console.error('Voice profile load error:', e);
    }
}

async function saveVoiceProfile() {
    const bio = document.getElementById('voice-bio').value;
    const preferred = document.getElementById('voice-preferred').value;
    const banned = document.getElementById('voice-banned').value;

    await fetch('/api/brain/voice-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            tone: 'Direct, knowledgeable builder, concrete numbers, no fluff',
            cadence: '1-2 sentence paragraphs with whitespace',
            preferred_phrases: preferred,
            banned_phrases: banned,
            cta_style: 'Specific question or closing numbered receipt',
            author_bio: bio
        })
    });
    alert('Voice profile updated in Brain!');
}

async function triggerReflection() {
    try {
        const res = await fetch('/api/brain/reflect', { method: 'POST' });
        const data = await res.json();
        const header = data.title || (data.status === 'skipped' ? 'Reflection Notice' : 'Reflection Complete');
        alert(header + ':\n\n' + (data.analysis || data.message || 'Complete'));
        loadReflections();
    } catch (e) {
        alert('Reflection error: ' + e);
    }
}

async function loadReflections() {
    try {
        const res = await fetch('/api/brain/reflections');
        const refs = await res.json();
        const container = document.getElementById('reflection-history');
        if (container) {
            container.innerHTML = refs.map(r => `
                <div class="p-3 bg-dark-900 rounded-xl border border-dark-700/60 text-xs space-y-1">
                    <div class="font-bold text-slate-200">${r.title}</div>
                    <p class="text-slate-300">${r.learnings}</p>
                    <div class="text-[10px] text-slate-500">${r.created_at}</div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Reflections error:', e);
    }
}

// 4. PROFILE OPTIMIZER
async function optimizeProfile() {
    const notes = document.getElementById('profile-notes').value.trim();
    const btn = document.getElementById('btn-optimize-profile');
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Optimizing 9 Points...`;
    btn.disabled = true;

    try {
        const res = await fetch('/api/profile/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes_or_profile: notes })
        });
        const data = await res.json();
        currentProfileDraft = data;

        document.getElementById('profile-optimized-output').innerText = data.optimized_content;

        // Render scorecard
        const scoreList = document.getElementById('scorecard-list');
        if (data.scorecard && scoreList) {
            scoreList.innerHTML = data.scorecard.map(s => `
                <div class="flex items-center justify-between p-2 rounded-lg bg-dark-900 border border-dark-700/50">
                    <span class="font-medium text-slate-300">${s.section}</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-mono ${s.status === 'optimized' || s.status === 'pass' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}">${s.status}</span>
                </div>
            `).join('');
        }
    } catch (e) {
        alert('Profile optimization failed: ' + e);
    } finally {
        btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i> Run 9-Point Profile Optimization`;
        btn.disabled = false;
        lucide.createIcons();
    }
}

function copyProfileText() {
    if (!currentProfileDraft) return;
    navigator.clipboard.writeText(currentProfileDraft.optimized_content);
    alert('Optimized profile text copied to clipboard!');
}

function extractProfileSections(text) {
    let headline = '';
    let about = '';
    if (!text) return { headline, about };

    const headlineMatch = text.match(/(?:###\s*1\.\s*HEADLINE[^\n]*\n+|HEADLINE[:\s]*\n+)([\s\S]*?)(?=\n###|\n\n###|$)/i);
    if (headlineMatch) {
        headline = headlineMatch[1].trim().split('\n')[0].replace(/^[\*\-_`\s]+|[\*\-_`\s]+$/g, '');
    }
    const aboutMatch = text.match(/(?:###\s*2\.\s*ABOUT[^\n]*\n+|ABOUT SECTION[:\s]*\n+)([\s\S]*?)(?=\n###|\n\n###|$)/i);
    if (aboutMatch) {
        about = aboutMatch[1].trim();
    }
    return { headline, about };
}

async function applyProfile() {
    if (!currentProfileDraft) {
        alert('Run optimization first.');
        return;
    }
    const { headline, about } = extractProfileSections(currentProfileDraft.optimized_content);
    const finalHeadline = headline || 'Founder & Software Architect | Sultrix Trade OS, Shadow Stream & Raulf International';

    const res = await fetch('/api/profile/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headline: finalHeadline, about: about })
    });
    const data = await res.json();
    alert(`Status: ${data.status}\n${data.message}`);
    if (data.profile_url) window.open(data.profile_url, '_blank');
}

function copyCommentReply(text, btnId) {
    navigator.clipboard.writeText(text);
    const btn = document.getElementById(btnId);
    if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i> Copied';
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
            btn.innerHTML = orig;
            if (window.lucide) lucide.createIcons();
        }, 2000);
    }
}

// 5. COMMENT SWEEPER
async function runCommentSweep() {
    const rawInput = document.getElementById('comment-post-url')?.value?.trim();
    const postContext = rawInput || (currentPostDraft && currentPostDraft.topic ? currentPostDraft.topic : 'Built Sultrix Trade OS with custom order routing. Latency reduced from 1.2s to 420ms.');
    const resultsContainer = document.getElementById('sweep-results');
    resultsContainer.innerHTML = `<div class="text-xs text-blue-400 animate-pulse">Sweeping thread comments, applying 2-level flattening and filtering rules...</div>`;

    try {
        const res = await fetch('/api/comments/sweep', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_context: postContext,
                sample_comments: [
                    { author: 'Marcus Vance', text: 'How do you handle WebSocket connection drops under heavy volatility?', depth: 1, top_level_urn: 'urn:li:comment:101' },
                    { author: 'Elena Rostova', text: 'great post thanks for sharing', depth: 1 },
                    { author: 'David Kim', text: 'Are you using Rust or Python for the trade execution core?', depth: 2, top_level_urn: 'urn:li:comment:101' }
                ]
            })
        });

        const data = await res.json();
        resultsContainer.innerHTML = `
            <div class="p-3 bg-dark-900 rounded-xl border border-dark-700 space-y-3">
                <div class="flex items-center justify-between text-xs">
                    <span class="text-slate-400">Total Scanned: <strong>${data.total_comments}</strong></span>
                    <span class="text-emerald-400">Filtered Spam: <strong>${data.filtered_count}</strong></span>
                    <span class="text-blue-400">Actionable Drafts: <strong>${data.actionable_count}</strong></span>
                </div>
                <div class="space-y-2">
                    ${data.drafts.map((d, idx) => `
                        <div class="p-3 bg-dark-800 rounded-lg border border-dark-700/60 text-xs space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-slate-200">${escapeHtml(d.commenter)}</span>
                                <span class="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded font-mono">React: ${escapeHtml(d.suggested_reaction)}</span>
                            </div>
                            <div class="text-slate-400 italic">"${escapeHtml(d.comment_text)}"</div>
                            <div class="text-slate-200 bg-dark-900/60 p-2.5 rounded border border-dark-700/50 flex items-start justify-between gap-2">
                                <div class="flex-1"><strong>Reply:</strong> ${escapeHtml(d.reply_draft)}</div>
                                <button id="btn-copy-reply-${idx}" onclick="copyCommentReply('${escapeHtml(d.reply_draft).replace(/'/g, "\\'")}', 'btn-copy-reply-${idx}')" class="px-2 py-1 bg-dark-700 hover:bg-dark-600 text-blue-400 rounded text-[11px] font-medium shrink-0 flex items-center gap-1 transition">
                                    <i data-lucide="copy" class="w-3 h-3"></i> Copy
                                </button>
                            </div>
                            <div class="text-[10px] text-slate-500">Parent URN: ${escapeHtml(d.parent_comment_urn || 'Top-level')}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        lucide.createIcons();
    } catch (e) {
        resultsContainer.innerHTML = `<div class="text-xs text-rose-400">Sweep error: ${e.message}</div>`;
    }
}

// 6. INBOX / DMS
window.currentDMReply = '';

function copyCurrentDM() {
    if (window.currentDMReply) {
        navigator.clipboard.writeText(window.currentDMReply);
        alert('Copied reply to clipboard!');
    }
}

async function processDM() {
    const sender = document.getElementById('dm-sender').value;
    const text = document.getElementById('dm-text').value;
    const card = document.getElementById('dm-response-card');
    card.innerHTML = `<div class="text-xs text-blue-400 animate-pulse">Classifying intent and drafting human reply...</div>`;

    try {
        const res = await fetch('/api/inbox/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sender_name: sender,
                sender_title: 'VP of Engineering',
                message_text: text
            })
        });
        const data = await res.json();
        window.currentDMReply = data.reply_draft;

        card.innerHTML = `
            <div class="flex items-center justify-between pb-2 border-b border-dark-700">
                <span class="text-slate-300 font-semibold">${data.sender_name}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30 uppercase">Intent: ${data.intent}</span>
            </div>
            <div class="text-slate-300 leading-relaxed whitespace-pre-wrap">${data.reply_draft}</div>
            <div class="flex justify-end gap-2 pt-2">
                <button onclick="copyCurrentDM()" class="px-3 py-1.5 bg-dark-700 hover:bg-dark-600 text-slate-200 rounded-lg text-xs font-semibold flex items-center gap-1 transition">
                    <i data-lucide="copy" class="w-3.5 h-3.5"></i> Copy Text
                </button>
                <button onclick="sendAutomatedDM('${escapeHtml(data.sender_name).replace(/'/g, "\\'")}')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition">
                    <i data-lucide="send" class="w-3.5 h-3.5"></i> Send via Browser
                </button>
            </div>
        `;
        lucide.createIcons();
    } catch (e) {
        card.innerHTML = `<div class="text-xs text-rose-400">DM error: ${e.message}</div>`;
    }
}

async function sendAutomatedDM(recipient) {
    if (!window.currentDMReply) {
        alert('No draft reply available.');
        return;
    }
    try {
        const res = await fetch('/api/inbox/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ recipient: recipient, message_text: window.currentDMReply })
        });
        const data = await res.json();
        alert(`Status: ${data.status}\n${data.message}`);
    } catch (e) {
        alert('Send DM error: ' + e);
    }
}

// 7. CONTENT PLANNER
async function generatePlan() {
    const output = document.getElementById('planner-output');
    output.innerText = 'Drafting 7-day multi-pillar editorial plan with 2026 hook formulas...';
    try {
        const res = await fetch('/api/planner/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                focus_topic: 'AI Agents, High-Concurrency Video Streaming, and High-Performance Trading Systems'
            })
        });
        const data = await res.json();
        output.innerText = data.weekly_plan;
    } catch (e) {
        output.innerText = 'Planner error: ' + e;
    }
}

// 8. SETTINGS & MULTI-PROVIDER ENGINE
function checkCustomModelVisibility() {
    const modelSelect = document.getElementById('setting-model');
    const customContainer = document.getElementById('custom-model-container');
    if (modelSelect && customContainer) {
        if (modelSelect.value === 'custom') {
            customContainer.classList.remove('hidden');
        } else {
            customContainer.classList.add('hidden');
        }
    }
}

function onProviderChanged() {
    const providerSelect = document.getElementById('setting-provider');
    const prov = providerSelect ? providerSelect.value : 'openrouter';

    // Hide all provider panels
    document.querySelectorAll('.provider-panel').forEach(el => el.classList.add('hidden'));

    // Show active panel
    const targetPanel = document.getElementById(`panel-provider-${prov}`);
    if (targetPanel) targetPanel.classList.remove('hidden');

    // Update status badge
    const badge = document.getElementById('provider-status-badge');
    if (badge) {
        const labels = {
            'ollama': 'Ollama (Local)',
            'openrouter': 'OpenRouter',
            'openai': 'Direct OpenAI',
            'anthropic': 'Direct Anthropic',
            'gemini': 'Direct Gemini',
            'custom': 'Custom Endpoint'
        };
        badge.innerText = labels[prov] || prov.toUpperCase();
    }

    if (prov === 'ollama') {
        refreshOllamaModels();
    }
}

async function refreshOllamaModels() {
    const statusEl = document.getElementById('ollama-live-status');
    const modelSelect = document.getElementById('setting-ollama-model');
    const baseUrlInput = document.getElementById('setting-ollama-url');
    const baseUrl = baseUrlInput ? baseUrlInput.value.trim() : 'http://localhost:11434';

    if (statusEl) statusEl.innerText = 'Probing local daemon...';

    try {
        const res = await fetch(`/api/settings/ollama-models?base_url=${encodeURIComponent(baseUrl)}`);
        const data = await res.json();

        if (data.connected && data.models && data.models.length > 0) {
            if (statusEl) {
                statusEl.innerText = `✓ Connected (${data.count} models available)`;
                statusEl.className = 'text-[11px] font-mono text-emerald-400';
            }
            if (modelSelect) {
                const currentVal = modelSelect.value;
                modelSelect.innerHTML = data.models.map(m => `
                    <option value="${escapeHtml(m)}">${escapeHtml(m)}</option>
                `).join('');
                if (currentVal && data.models.includes(currentVal)) {
                    modelSelect.value = currentVal;
                }
            }
        } else {
            if (statusEl) {
                statusEl.innerText = '⚠️ Offline / No models found';
                statusEl.className = 'text-[11px] font-mono text-amber-400';
            }
        }
    } catch (e) {
        if (statusEl) {
            statusEl.innerText = '⚠️ Cannot reach daemon';
            statusEl.className = 'text-[11px] font-mono text-rose-400';
        }
    }
}

async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const data = await res.json();

        // Active Provider
        const provSelect = document.getElementById('setting-provider');
        if (provSelect && data.llm_provider) {
            provSelect.value = data.llm_provider;
            onProviderChanged();
        }

        // OpenRouter Model selector
        const modelSelect = document.getElementById('setting-model');
        const customContainer = document.getElementById('custom-model-container');
        const customInput = document.getElementById('setting-custom-model');

        if (modelSelect && data.openrouter_model) {
            const cur = data.openrouter_model;
            const options = Array.from(modelSelect.querySelectorAll('option')).map(o => o.value);
            if (options.includes(cur)) {
                modelSelect.value = cur;
                if (customContainer) customContainer.classList.add('hidden');
            } else {
                modelSelect.value = 'custom';
                if (customContainer) customContainer.classList.remove('hidden');
                if (customInput) customInput.value = cur;
            }
        }

        // OpenAI Model
        const openaiModelSelect = document.getElementById('setting-openai-model');
        if (openaiModelSelect && data.openai_model) openaiModelSelect.value = data.openai_model;
        const openaiKeyStatus = document.getElementById('openai-key-status');
        if (openaiKeyStatus) {
            openaiKeyStatus.innerText = data.openai_api_key_set ? '✓ Key Active' : 'Not Set';
            openaiKeyStatus.className = data.openai_api_key_set ? 'text-[11px] font-mono text-emerald-400' : 'text-[11px] font-mono text-slate-400';
        }

        // Anthropic Model
        const anthropicModelSelect = document.getElementById('setting-anthropic-model');
        if (anthropicModelSelect && data.anthropic_model) anthropicModelSelect.value = data.anthropic_model;
        const anthropicKeyStatus = document.getElementById('anthropic-key-status');
        if (anthropicKeyStatus) {
            anthropicKeyStatus.innerText = data.anthropic_api_key_set ? '✓ Key Active' : 'Not Set';
            anthropicKeyStatus.className = data.anthropic_api_key_set ? 'text-[11px] font-mono text-emerald-400' : 'text-[11px] font-mono text-slate-400';
        }

        // Gemini Model
        const geminiModelSelect = document.getElementById('setting-gemini-model');
        if (geminiModelSelect && data.gemini_model) geminiModelSelect.value = data.gemini_model;
        const geminiKeyStatus = document.getElementById('gemini-key-status');
        if (geminiKeyStatus) {
            geminiKeyStatus.innerText = data.gemini_api_key_set ? '✓ Key Active' : 'Not Set';
            geminiKeyStatus.className = data.gemini_api_key_set ? 'text-[11px] font-mono text-emerald-400' : 'text-[11px] font-mono text-slate-400';
        }

        // Ollama Settings
        const ollamaUrlInput = document.getElementById('setting-ollama-url');
        if (ollamaUrlInput && data.ollama_base_url) ollamaUrlInput.value = data.ollama_base_url;
        const ollamaModelSelect = document.getElementById('setting-ollama-model');
        if (ollamaModelSelect && data.ollama_models && data.ollama_models.length > 0) {
            ollamaModelSelect.innerHTML = data.ollama_models.map(m => `
                <option value="${escapeHtml(m)}">${escapeHtml(m)}</option>
            `).join('');
            if (data.ollama_model) ollamaModelSelect.value = data.ollama_model;
        }

        // Custom Settings
        const customUrlInput = document.getElementById('setting-custom-url');
        if (customUrlInput && data.custom_base_url) customUrlInput.value = data.custom_base_url;
        const customModelInput = document.getElementById('setting-custom-model-name');
        if (customModelInput && data.custom_model) customModelInput.value = data.custom_model;

        // Mode and Vision selector
        const modeSelect = document.getElementById('setting-mode');
        if (modeSelect && data.execution_mode) modeSelect.value = data.execution_mode;
        const visionSelect = document.getElementById('setting-vision-model');
        if (visionSelect && data.vision_model) visionSelect.value = data.vision_model;


        // Active model badge in sidebar or header
        const activeBadge = document.getElementById('active-model-badge');
        if (activeBadge) {
            const activeM = data.llm_provider === 'ollama' ? (data.ollama_model || 'ollama') :
                            data.llm_provider === 'openai' ? (data.openai_model || 'openai') :
                            data.llm_provider === 'anthropic' ? (data.anthropic_model || 'claude') :
                            data.llm_provider === 'gemini' ? (data.gemini_model || 'gemini') :
                            (data.openrouter_model ? data.openrouter_model.split('/').pop().replace(':free', '') : 'openrouter');
            activeBadge.innerText = `${data.llm_provider}: ${activeM}`;
        }

        // API Key status for OpenRouter
        const apiKeyStatus = document.getElementById('api-key-status');
        if (apiKeyStatus) {
            apiKeyStatus.innerText = data.openrouter_api_key_set ? '✓ Key Active' : '⚠️ Key Missing';
            apiKeyStatus.className = data.openrouter_api_key_set ? 'text-[11px] font-mono text-emerald-400' : 'text-[11px] font-mono text-amber-400';
        }

        // Browser Authentication Status & Method
        const browserStatus = document.getElementById('browser-auth-status');
        const disconnectBtn = document.getElementById('btn-disconnect');
        if (browserStatus) {
            if (data.browser_authenticated) {
                const methodLabel = data.auth_method === 'li_at_cookie' ? 'li_at Cookie' : 'Browser Session';
                browserStatus.innerText = `✓ Connected (${methodLabel})`;
                browserStatus.className = 'text-xs px-2.5 py-1 rounded-full font-mono bg-emerald-500/10 border border-emerald-500/30 text-emerald-400';
                if (disconnectBtn) disconnectBtn.classList.remove('hidden');
            } else {
                browserStatus.innerText = '⚠️ Not Connected';
                browserStatus.className = 'text-xs px-2.5 py-1 rounded-full font-mono bg-amber-500/10 border border-amber-500/30 text-amber-400';
                if (disconnectBtn) disconnectBtn.classList.add('hidden');
            }
        }
    } catch (e) {
        console.error('Error loading settings:', e);
    }
}

async function saveSettings() {
    const provider = document.getElementById('setting-provider')?.value || 'openrouter';

    let openrouterModel = document.getElementById('setting-model')?.value;
    if (openrouterModel === 'custom') {
        const customVal = document.getElementById('setting-custom-model')?.value?.trim();
        if (customVal) openrouterModel = customVal;
    }

    const payload = {
        llm_provider: provider,
        execution_mode: document.getElementById('setting-mode')?.value || 'manual',
        openrouter_model: openrouterModel,
        openai_model: document.getElementById('setting-openai-model')?.value,
        anthropic_model: document.getElementById('setting-anthropic-model')?.value,
        gemini_model: document.getElementById('setting-gemini-model')?.value,
        ollama_model: document.getElementById('setting-ollama-model')?.value,
        ollama_base_url: document.getElementById('setting-ollama-url')?.value?.trim(),
        custom_base_url: document.getElementById('setting-custom-url')?.value?.trim(),
        custom_model: document.getElementById('setting-custom-model-name')?.value?.trim(),
        vision_model: document.getElementById('setting-vision-model')?.value
    };

    const openrouterKey = document.getElementById('setting-api-key')?.value?.trim();
    if (openrouterKey) payload.openrouter_api_key = openrouterKey;

    const openaiKey = document.getElementById('setting-openai-key')?.value?.trim();
    if (openaiKey) payload.openai_api_key = openaiKey;

    const anthropicKey = document.getElementById('setting-anthropic-key')?.value?.trim();
    if (anthropicKey) payload.anthropic_api_key = anthropicKey;

    const geminiKey = document.getElementById('setting-gemini-key')?.value?.trim();
    if (geminiKey) payload.gemini_api_key = geminiKey;

    const customKey = document.getElementById('setting-custom-key')?.value?.trim();
    if (customKey) payload.custom_api_key = customKey;

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert('Settings saved and persisted to database!');
        loadSettings();
    } catch (e) {
        alert('Failed to save settings: ' + e);
    }
}

// AI Assistant Config Clipboard Helpers
function copyClaudeDesktopConfig() {
    const config = {
        "mcpServers": {
            "linkedin-nexus": {
                "command": "python",
                "args": ["G:\\linkedin agent\\run_mcp.py"]
            }
        }
    };
    navigator.clipboard.writeText(JSON.stringify(config, null, 2));
    alert('Copied Claude Desktop configuration to clipboard!\nPaste into your claude_desktop_config.json file.');
}

function copyCursorConfig() {
    const config = {
        "mcpServers": {
            "linkedin-nexus": {
                "command": "python",
                "args": ["G:\\linkedin agent\\run_mcp.py"]
            }
        }
    };
    navigator.clipboard.writeText(JSON.stringify(config, null, 2));
    alert('Copied Cursor MCP configuration to clipboard!\nIn Cursor, open Settings -> MCP -> Add new MCP server.');
}

function copySkillCommand() {
    navigator.clipboard.writeText("python scripts/install_skill.py");
    alert('Copied command: "python scripts/install_skill.py"\nRun this command in terminal to register the skill.');
}

// Direct li_at Cookie Connection (Instant < 1s)
async function saveCookieSession() {
    const input = document.getElementById('setting-cookie-input');
    const cookieVal = input ? input.value.trim() : '';
    if (!cookieVal) {
        alert('Please paste your li_at cookie first.');
        return;
    }

    const btn = document.getElementById('btn-save-cookie');
    const originalHtml = btn ? btn.innerHTML : 'Save & Connect';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Verifying with LinkedIn...`;
        if (window.lucide) lucide.createIcons();
    }

    try {
        const res = await fetch('/api/settings/save-cookie', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cookie: cookieVal })
        });
        const data = await res.json();

        if (data.status === 'success') {
            alert('🎉 ' + data.message);
            if (input) input.value = '';
            await loadSettings();
        } else {
            alert('⚠️ ' + (data.message || 'Cookie verification failed.'));
        }
    } catch (e) {
        alert('Error connecting with cookie: ' + e.message);
    } finally {
        if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            if (window.lucide) lucide.createIcons();
        }
    }
}

async function disconnectSession() {
    if (!confirm('Are you sure you want to disconnect your LinkedIn session?')) return;
    try {
        const res = await fetch('/api/settings/disconnect', { method: 'POST' });
        const data = await res.json();
        alert(data.message || 'Session disconnected.');
        await loadSettings();
    } catch (e) {
        alert('Disconnect error: ' + e.message);
    }
}

function closeBrowserLoginModal() {
    const modal = document.getElementById('modal-browser-login');
    if (modal) modal.classList.add('hidden');
}

async function connectBrowser() {
    const modal = document.getElementById('modal-browser-login');
    if (modal) {
        modal.classList.remove('hidden');
        if (window.lucide) lucide.createIcons();
    }

    try {
        const res = await fetch('/api/settings/connect-browser', { method: 'POST' });
        const data = await res.json();

        closeBrowserLoginModal();
        if (data.status === 'success') {
            alert('🎉 ' + data.message);
        } else if (data.status === 'cancelled') {
            alert('ℹ️ ' + data.message);
        } else {
            alert('⚠️ ' + (data.message || 'Error launching browser session'));
        }
    } catch (e) {
        closeBrowserLoginModal();
        alert('Network/Server error while connecting browser: ' + e.message);
    } finally {
        await loadSettings();
    }
}

// 9. AGENT REACH & FEED EYES
async function scanLiveFeed() {
    const btn = document.getElementById('btn-scan-feed');
    const statusEl = document.getElementById('reach-scan-status');
    const originalHtml = btn ? btn.innerHTML : 'Scan Live Feed Now';

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Agent Eyes Active (Scanning Feed)...`;
        if (window.lucide) lucide.createIcons();
    }
    if (statusEl) statusEl.innerText = 'Scanning live feed...';

    try {
        const res = await fetch('/api/reach/scan-feed', { method: 'POST' });
        const data = await res.json();

        if (data.status === 'success') {
            if (statusEl) statusEl.innerText = `Scanned ${data.posts_found || 0} updates`;

            // Screenshot display
            if (data.screenshot_url) {
                const img = document.getElementById('feed-screenshot-img');
                const placeholder = document.getElementById('visual-placeholder');
                if (img) {
                    img.src = data.screenshot_url + '?t=' + Date.now();
                    img.classList.remove('hidden');
                }
                if (placeholder) placeholder.classList.add('hidden');
            }

            // Vision Cortex text
            const visionText = document.getElementById('vision-feedback-text');
            if (visionText && data.vision_analysis) {
                visionText.innerHTML = escapeHtml(data.vision_analysis).replace(/\n/g, '<br>');
            }

            // Render posts
            if (data.posts && data.posts.length > 0) {
                renderScannedFeed(data.posts);
            } else {
                loadScannedFeed();
            }
        } else if (data.status === 'auth_required') {
            alert('⚠️ ' + data.message);
            switchTab('settings');
        } else {
            alert('Feed scan error: ' + (data.message || 'Unknown error'));
        }
    } catch (e) {
        alert('Scan request failed: ' + e.message);
    } finally {
        if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            if (window.lucide) lucide.createIcons();
        }
    }
}

async function loadScannedFeed() {
    try {
        const res = await fetch('/api/reach/feed');
        const data = await res.json();
        if (data.posts) {
            renderScannedFeed(data.posts);
        }
    } catch (e) {
        console.error('Error loading scanned feed:', e);
    }
}

function renderScannedFeed(posts) {
    const list = document.getElementById('scanned-feed-list');
    const countEl = document.getElementById('scanned-count');
    if (countEl) countEl.innerText = posts.length;

    if (!list) return;
    if (posts.length === 0) {
        list.innerHTML = `
            <div class="col-span-full text-center py-8 text-xs text-slate-500">
                No scanned posts yet. Click "Scan Live Feed Now" to look into your LinkedIn feed.
            </div>
        `;
        return;
    }

    list.innerHTML = posts.map((p, idx) => {
        const author = escapeHtml(p.author_name || 'LinkedIn Member');
        const headline = escapeHtml(p.author_headline || '');
        const text = escapeHtml(p.post_text || '');
        const urn = escapeHtml(p.post_urn || p.post_url || '');
        const reactions = p.reaction_count || 0;
        const comments = p.comment_count || 0;

        return `
            <div class="bg-dark-900 border border-dark-700/80 rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-dark-600 transition">
                <div class="space-y-2">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <div class="font-bold text-xs text-slate-200 flex items-center gap-1.5">
                                <i data-lucide="user" class="w-3.5 h-3.5 text-blue-400"></i> ${author}
                            </div>
                            ${headline ? `<div class="text-[10px] text-slate-400 line-clamp-1">${headline}</div>` : ''}
                        </div>
                        <div class="flex items-center gap-2 text-[10px] text-slate-400 font-mono shrink-0">
                            <span title="Reactions" class="flex items-center gap-0.5"><i data-lucide="thumbs-up" class="w-3 h-3 text-blue-400"></i> ${reactions}</span>
                            <span title="Comments" class="flex items-center gap-0.5"><i data-lucide="message-square" class="w-3 h-3 text-cyan-400"></i> ${comments}</span>
                        </div>
                    </div>
                    <p class="text-xs text-slate-300 leading-relaxed line-clamp-4 whitespace-pre-wrap">${text}</p>
                </div>

                <div class="pt-2 border-t border-dark-700/50 flex flex-wrap items-center justify-between gap-2">
                    <button onclick="remixPostIntoStudio('${escapeHtml(author).replace(/'/g, "\\'")}', '${escapeHtml(text.slice(0, 120)).replace(/'/g, "\\'")}')" class="px-2.5 py-1 text-[11px] bg-dark-800 hover:bg-dark-700 text-purple-300 border border-purple-500/30 rounded-lg transition flex items-center gap-1 font-medium">
                        <i data-lucide="sparkles" class="w-3 h-3 text-purple-400"></i> Remix in Studio
                    </button>
                    <div class="flex items-center gap-1.5">
                        <button onclick="draftReplyForScannedPost('${escapeHtml(author).replace(/'/g, "\\'")}', '${escapeHtml(text.slice(0, 180)).replace(/'/g, "\\'")}')" class="px-2.5 py-1 text-[11px] bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-1 font-semibold">
                            <i data-lucide="message-circle" class="w-3 h-3"></i> Draft Reply
                        </button>
                        ${urn ? `
                        <button onclick="likeLinkedInPost('${urn.replace(/'/g, "\\'")}')" class="p-1.5 bg-dark-800 hover:bg-dark-700 text-slate-300 rounded-lg transition" title="Like on LinkedIn">
                            <i data-lucide="heart" class="w-3.5 h-3.5 text-rose-400"></i>
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    if (window.lucide) lucide.createIcons();
}

function remixPostIntoStudio(author, snippet) {
    switchTab('studio');
    const topicInput = document.getElementById('post-topic');
    if (topicInput) {
        topicInput.value = `Contrarian perspective on industry post by ${author}: "${snippet}..."`;
        topicInput.focus();
    }
}

function draftReplyForScannedPost(author, snippet) {
    switchTab('comments');
    const sweepBox = document.getElementById('comment-post-url');
    if (sweepBox) {
        sweepBox.value = `Perspective on post by ${author}: "${snippet}"`;
    }
    runCommentSweep();
}

async function likeLinkedInPost(postUrn) {
    try {
        const res = await fetch('/api/reach/like', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ post_urn: postUrn })
        });
        const data = await res.json();
        alert(data.message || 'Post liked!');
    } catch (e) {
        alert('Like error: ' + e.message);
    }
}

async function inspectUrlWithReach() {
    const input = document.getElementById('inspect-url-input');
    const url = input ? input.value.trim() : '';
    if (!url) {
        alert('Please enter a URL to inspect.');
        return;
    }

    const box = document.getElementById('inspect-result-box');
    const btn = document.getElementById('btn-inspect-url');
    const originalHtml = btn ? btn.innerHTML : 'Inspect';

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Reading...`;
        if (window.lucide) lucide.createIcons();
    }
    if (box) {
        box.innerHTML = `<div class="text-center py-10 text-xs text-blue-400 animate-pulse">Dual-Backend Reach engine reading URL and synthesizing strategic angles...</div>`;
    }

    try {
        const res = await fetch('/api/reach/inspect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await res.json();

        if (data.status === 'success') {
            box.innerHTML = `
                <div class="space-y-3">
                    <div class="flex items-center justify-between pb-2 border-b border-dark-700">
                        <h4 class="font-bold text-xs text-slate-100 line-clamp-1">${escapeHtml(data.title || 'Inspected Resource')}</h4>
                        <span class="text-[10px] px-2 py-0.5 rounded font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30 uppercase">${data.backend || 'jina'}</span>
                    </div>
                    <div class="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-sans">${escapeHtml(data.ai_analysis || data.raw_summary)}</div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button onclick="remixPostIntoStudio('Inspected Article', '${escapeHtml(data.title || '').replace(/'/g, "\\'")}')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition">
                            <i data-lucide="pen-tool" class="w-3.5 h-3.5"></i> Write Post on This Angle
                        </button>
                    </div>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        } else {
            box.innerHTML = `<div class="text-xs text-rose-400 p-4">Inspection error: ${escapeHtml(data.message || 'Failed to extract content')}</div>`;
        }
    } catch (e) {
        box.innerHTML = `<div class="text-xs text-rose-400 p-4">Request error: ${escapeHtml(e.message)}</div>`;
    } finally {
        if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            if (window.lucide) lucide.createIcons();
        }
    }
}

// 10. GITHUB SEO AGENT
let cachedLaunchPacks = null;
let currentLaunchChannel = 'hacker_news';

async function loadGitHubSEOAudit() {
    const scoreEl = document.getElementById('seo-score');
    const gradeEl = document.getElementById('seo-grade');
    const checklistEl = document.getElementById('seo-checklist');
    const topicsEl = document.getElementById('seo-topics-container');
    const cliBox = document.getElementById('seo-cli-box');
    const btn = document.getElementById('btn-run-seo-audit');

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Auditing...`;
        if (window.lucide) lucide.createIcons();
    }

    try {
        const res = await fetch('/api/seo/audit');
        const data = await res.json();

        if (scoreEl) scoreEl.innerText = data.score;
        if (gradeEl) gradeEl.innerText = `Grade ${data.grade}`;

        if (checklistEl && data.checklist) {
            checklistEl.innerHTML = data.checklist.map(item => {
                const icon = item.status === 'pass'
                    ? '<i data-lucide="check" class="w-4 h-4 text-emerald-400 shrink-0"></i>'
                    : (item.status === 'warning'
                        ? '<i data-lucide="alert-triangle" class="w-4 h-4 text-amber-400 shrink-0"></i>'
                        : '<i data-lucide="x-circle" class="w-4 h-4 text-rose-400 shrink-0"></i>');

                const badgeClass = item.status === 'pass'
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : (item.status === 'warning'
                        ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                        : 'bg-rose-500/20 text-rose-400 border-rose-500/30');

                return `
                    <div class="p-2.5 rounded-xl bg-dark-900 border border-dark-700/60 flex items-start gap-2.5">
                        <div class="mt-0.5">${icon}</div>
                        <div class="space-y-0.5 flex-1 min-w-0">
                            <div class="flex items-center justify-between gap-1">
                                <span class="font-bold text-slate-200 text-xs">${escapeHtml(item.item)}</span>
                                <span class="text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase ${badgeClass}">${item.status}</span>
                            </div>
                            <p class="text-[11px] text-slate-400 leading-relaxed">${escapeHtml(item.note)}</p>
                        </div>
                    </div>
                `;
            }).join('');
        }

        if (topicsEl && data.recommended_topics) {
            topicsEl.innerHTML = data.recommended_topics.map(t => `
                <span class="px-2 py-0.5 rounded-lg font-mono text-[10px] bg-dark-700 text-slate-300 border border-dark-600">
                    #${escapeHtml(t)}
                </span>
            `).join('');
        }

        if (cliBox && data.gh_cli_command) {
            cliBox.innerText = data.gh_cli_command;
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('SEO Audit error:', e);
    } finally {
        if (btn) {
            btn.innerHTML = `<i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-blue-400"></i> Run Audit`;
            btn.disabled = false;
            if (window.lucide) lucide.createIcons();
        }
    }
}

async function selectLaunchChannel(channel) {
    currentLaunchChannel = channel;

    // Toggle button styling
    document.querySelectorAll('.launch-channel-btn').forEach(btn => {
        btn.classList.remove('text-slate-200', 'bg-dark-700', 'border', 'border-dark-600');
        btn.classList.add('text-slate-400');
    });

    const activeBtn = document.getElementById(`channel-btn-${channel}`);
    if (activeBtn) {
        activeBtn.classList.add('text-slate-200', 'bg-dark-700', 'border', 'border-dark-600');
        activeBtn.classList.remove('text-slate-400');
    }

    const textarea = document.getElementById('seo-launch-text');

    if (cachedLaunchPacks && cachedLaunchPacks[channel]) {
        if (textarea) textarea.value = cachedLaunchPacks[channel];
        return;
    }

    if (textarea) textarea.value = 'Generating tailored launch copy for ' + channel + '...';

    try {
        const res = await fetch('/api/seo/launch-pack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel: 'all' })
        });
        const data = await res.json();
        if (data.packs) {
            cachedLaunchPacks = data.packs;
            if (textarea && cachedLaunchPacks[channel]) {
                textarea.value = cachedLaunchPacks[channel];
            }
        }
    } catch (e) {
        if (textarea) textarea.value = 'Failed to load launch copy: ' + e.message;
    }
}

function copyLaunchPackText() {
    const textarea = document.getElementById('seo-launch-text');
    const copyBtn = document.getElementById('btn-copy-launch-pack');
    if (!textarea || !textarea.value) return;

    navigator.clipboard.writeText(textarea.value);

    if (copyBtn) {
        const orig = copyBtn.innerHTML;
        copyBtn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-300"></i> Copied to Clipboard!`;
        copyBtn.classList.add('bg-emerald-600');
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
            copyBtn.innerHTML = orig;
            copyBtn.classList.remove('bg-emerald-600');
            if (window.lucide) lucide.createIcons();
        }, 2000);
    }
}

function copyTopicsCommand() {
    const cliBox = document.getElementById('seo-cli-box');
    if (cliBox) {
        navigator.clipboard.writeText(cliBox.innerText.trim());
        alert('Copied GitHub CLI command to clipboard!\nRun this in your terminal to tag your repository with high-intent topics.');
    }
}

async function applyOptimizedReadme() {
    if (!confirm('This will update README.md with the 100% SEO-optimized version (a backup README.md.backup will be created). Continue?')) return;

    const btn = document.getElementById('btn-apply-seo-readme');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Applying...`;
        if (window.lucide) lucide.createIcons();
    }

    try {
        const res = await fetch('/api/seo/optimize-readme', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ apply: true })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert('🎉 README.md successfully updated with the 100% SEO-optimized version!\nOriginal version safely backed up to README.md.backup.');
            await loadGitHubSEOAudit();
        } else {
            alert('Error updating README: ' + (data.message || 'Unknown error'));
        }
    } catch (e) {
        alert('Request failed: ' + e.message);
    } finally {
        if (btn) {
            btn.innerHTML = `<i data-lucide="file-check" class="w-3.5 h-3.5"></i> Apply SEO README`;
            btn.disabled = false;
            if (window.lucide) lucide.createIcons();
        }
    }
}

async function installCommunityHealthFiles() {
    const btn = document.getElementById('btn-install-community');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Installing...`;
        if (window.lucide) lucide.createIcons();
    }

    try {
        const res = await fetch('/api/seo/install-community-files', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            alert('🎉 ' + data.message + '\nFiles:\n' + data.files_written.join('\n'));
            await loadGitHubSEOAudit();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        alert('Request failed: ' + e.message);
    } finally {
        if (btn) {
            btn.innerHTML = `<i data-lucide="shield-check" class="w-3.5 h-3.5"></i> Install Community Files`;
            btn.disabled = false;
            if (window.lucide) lucide.createIcons();
        }
    }
}

