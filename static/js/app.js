// NexusAgent - Autonomous LinkedIn Studio Application Logic

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

    // Save and publish
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
                status: 'published'
            })
        });
        const saved = await saveRes.json();
        const pubRes = await fetch(`/api/posts/publish/${saved.post_id}`, { method: 'POST' });
        const pubData = await pubRes.json();

        await loadSavedDrafts();
        alert(`✅ Post text copied to clipboard!\nStatus: ${pubData.dispatch_result?.status || 'published'}\n${pubData.dispatch_result?.message || ''}`);
        if (pubData.dispatch_result?.linkedin_composer_url) {
            window.open(pubData.dispatch_result.linkedin_composer_url, '_blank');
        }
    } catch (e) {
        alert('Publish error: ' + e);
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
    if (document.getElementById('post-formula') && post.hook_formula) {
        const code = post.hook_formula.split(' ')[0].trim();
        const sel = document.getElementById('post-formula');
        for (let i = 0; i < sel.options.length; i++) {
            if (sel.options[i].value === code) {
                sel.selectedIndex = i;
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

// 5. COMMENT SWEEPER
async function runCommentSweep() {
    const postUrl = document.getElementById('comment-post-url').value.trim() || 'https://www.linkedin.com/posts/activity-7448808898326654978';
    const resultsContainer = document.getElementById('sweep-results');
    resultsContainer.innerHTML = `<div class="text-xs text-blue-400 animate-pulse">Sweeping thread comments, applying 2-level flattening and filtering rules...</div>`;

    try {
        const res = await fetch('/api/comments/sweep', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_context: 'Built Sultrix Trade OS with custom order routing. Latency reduced from 1.2s to 420ms.',
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
                    <span class="text-blue-400">Drafted: <strong>${data.actionable_count}</strong></span>
                </div>
                <div class="space-y-2">
                    ${data.drafts.map(d => `
                        <div class="p-3 bg-dark-800 rounded-lg border border-dark-700/60 text-xs space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-slate-200">${d.commenter}</span>
                                <span class="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded font-mono">React: ${d.suggested_reaction}</span>
                            </div>
                            <div class="text-slate-400 italic">"${d.comment_text}"</div>
                            <div class="text-slate-200 bg-dark-900/60 p-2 rounded border border-dark-700/50"><strong>Reply:</strong> ${d.reply_draft}</div>
                            <div class="text-[10px] text-slate-500">Parent URN: ${d.parent_comment_urn || 'Top-level'}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
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
                <button onclick="copyCurrentDM()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold">Copy & Send</button>
            </div>
        `;
    } catch (e) {
        card.innerHTML = `<div class="text-xs text-rose-400">DM error: ${e.message}</div>`;
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

// 8. SETTINGS
async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const data = await res.json();

        // Model selector
        const modelSelect = document.getElementById('setting-model');
        if (modelSelect && data.available_free_models) {
            const existingVals = Array.from(modelSelect.options).map(o => o.value);
            data.available_free_models.forEach(m => {
                if (!existingVals.includes(m)) {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.innerText = m;
                    modelSelect.appendChild(opt);
                }
            });
            if (data.openrouter_model) {
                modelSelect.value = data.openrouter_model;
            }
        }

        // Mode selector
        const modeSelect = document.getElementById('setting-mode');
        if (modeSelect && data.execution_mode) {
            modeSelect.value = data.execution_mode;
        }

        // Active model badge in sidebar or header
        const activeBadge = document.getElementById('active-model-badge');
        if (activeBadge && data.openrouter_model) {
            activeBadge.innerText = data.openrouter_model.split('/').pop().replace(':free', '');
        }

        // API Key status
        const apiKeyStatus = document.getElementById('api-key-status');
        if (apiKeyStatus) {
            if (data.openrouter_api_key_set) {
                apiKeyStatus.innerText = '✓ Key Active';
                apiKeyStatus.className = 'text-[11px] font-mono text-emerald-400';
            } else {
                apiKeyStatus.innerText = '⚠️ Key Missing';
                apiKeyStatus.className = 'text-[11px] font-mono text-amber-400';
            }
        }
    } catch (e) {
        console.error('Error loading settings:', e);
    }
}

async function saveSettings() {
    const model = document.getElementById('setting-model').value;
    const mode = document.getElementById('setting-mode').value;
    const apiKey = document.getElementById('setting-api-key')?.value?.trim();

    const payload = { openrouter_model: model, execution_mode: mode };
    if (apiKey) payload.openrouter_api_key = apiKey;

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        const activeBadge = document.getElementById('active-model-badge');
        if (activeBadge) activeBadge.innerText = model.split('/').pop().replace(':free', '');
        if (apiKey) {
            const keyInput = document.getElementById('setting-api-key');
            if (keyInput) keyInput.value = '';
        }
        alert('Settings saved and persisted to database!');
        loadSettings();
    } catch (e) {
        alert('Failed to save settings: ' + e);
    }
}

async function connectBrowser() {
    alert('Opening browser session. Please log in to LinkedIn if prompted. Your session will be stored locally.');
    await fetch('/api/settings/connect-browser', { method: 'POST' });
}
