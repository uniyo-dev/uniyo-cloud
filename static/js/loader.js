// ============================================
// UNIYO LMS - Complete Loader System
// Brand Violet: #6D28D9
// ============================================

const UNIYO_LOADER = {

    // ==========================================
    // 1. APP LAUNCH
    // ==========================================
    appLaunch: {
        frames: ['ldFrame1', 'ldFrame2', 'ldFrame3', 'ldFrame4', 'ldFrame5'],
        dots: ['ldDot1', 'ldDot2', 'ldDot3', 'ldDot4', 'ldDot5'],
        current: 0,
        interval: null,

        show() {
            const overlay = document.getElementById('ldLaunch');
            if (!overlay) return;
            overlay.classList.remove('hidden');
            this.current = 0;
            this.showFrame(0);

            const intro = document.getElementById('ldLaunchIntro');
            const story = document.getElementById('ldLaunchStory');
            const dots = document.getElementById('ldLaunchDots');

            if (intro) intro.classList.remove('hidden');
            if (story) { story.style.opacity = '0'; story.style.pointerEvents = 'none'; }
            if (dots) dots.style.opacity = '0';

            const self = this;
            setTimeout(function() {
                if (intro) intro.classList.add('hidden');
                if (story) { story.style.opacity = '1'; story.style.pointerEvents = 'auto'; }
                if (dots) dots.style.opacity = '1';
                self.startAutoPlay();
            }, 2000);
        },

        showFrame(index) {
            const self = this;
            this.frames.forEach(function(f) {
                const el = document.getElementById(f);
                if (el) el.classList.remove('active');
            });
            const currentFrame = document.getElementById(this.frames[index]);
            if (currentFrame) currentFrame.classList.add('active');

            this.dots.forEach(function(d, i) {
                const el = document.getElementById(d);
                if (el) el.classList.toggle('active', i === index);
            });
            this.current = index;
        },

        startAutoPlay() {
            const self = this;
            clearInterval(this.interval);
            this.interval = setInterval(function() {
                if (self.current < self.frames.length - 1) {
                    self.showFrame(self.current + 1);
                } else {
                    clearInterval(self.interval);
                    setTimeout(function() { self.hide(); }, 1000);
                }
            }, 2500);
        },

        skip() {
            clearInterval(this.interval);
            this.hide();
        },

        hide() {
            const overlay = document.getElementById('ldLaunch');
            if (overlay) overlay.classList.add('hidden');
            clearInterval(this.interval);
        }
    },

    // ==========================================
    // 2. REGISTRATION (Phone + Password Verify)
    // ==========================================
    registration: {
        steps: ['ldRegStep1', 'ldRegStep2', 'ldRegStep3', 'ldRegStep4', 'ldRegStep5'],
        current: 0,
        CORRECT_PHONE: '0912345678',
        CORRECT_PASSWORD: 'Abebe@2024',

        show() {
            const overlay = document.getElementById('ldRegistration');
            if (!overlay) return;
            overlay.classList.remove('hidden');
            this.current = 0;
            this.showStep(0);
            this.updateProgress(0);

            const phoneInput = document.getElementById('ldRegPhone');
            const passwordInput = document.getElementById('ldRegPassword');
            const phoneBtn = document.getElementById('ldRegPhoneBtn');
            const passwordBtn = document.getElementById('ldRegPasswordBtn');

            if (phoneInput) { phoneInput.value = ''; phoneInput.classList.remove('error', 'success'); }
            if (passwordInput) { passwordInput.value = ''; passwordInput.classList.remove('error', 'success'); }
            if (phoneBtn) phoneBtn.disabled = true;
            if (passwordBtn) passwordBtn.disabled = true;
        },

        showStep(index) {
            const self = this;
            this.steps.forEach(function(s) {
                const el = document.getElementById(s);
                if (el) el.classList.remove('active');
            });
            const currentStep = document.getElementById(this.steps[index]);
            if (currentStep) currentStep.classList.add('active');
            this.current = index;

            const counter = document.getElementById('ldRegCounter');
            if (counter) counter.textContent = 'STEP ' + (index + 1) + ' OF 5';
        },

        updateProgress(index) {
            const fill = document.getElementById('ldRegProgress');
            if (fill) fill.style.width = ((index + 1) / this.steps.length * 100) + '%';
        },

        verifyPhone() {
            const self = this;
            const input = document.getElementById('ldRegPhone');
            if (!input) return;
            if (input.value === this.CORRECT_PHONE) {
                input.classList.add('success');
                setTimeout(function() {
                    self.showStep(1);
                    self.updateProgress(1);
                }, 400);
            } else {
                input.classList.add('error');
                setTimeout(function() { input.classList.remove('error'); }, 1200);
            }
        },

        verifyPassword() {
            const self = this;
            const input = document.getElementById('ldRegPassword');
            if (!input) return;
            if (input.value === this.CORRECT_PASSWORD) {
                input.classList.add('success');
                setTimeout(function() {
                    self.showStep(2);
                    self.updateProgress(2);
                    self.startAutoAdvance();
                }, 400);
            } else {
                input.classList.add('error');
                setTimeout(function() { input.classList.remove('error'); }, 1200);
            }
        },

        startAutoAdvance() {
            const self = this;
            clearInterval(this.interval);
            this.interval = setInterval(function() {
                if (self.current < self.steps.length - 1) {
                    self.showStep(self.current + 1);
                    self.updateProgress(self.current);
                } else {
                    clearInterval(self.interval);
                    setTimeout(function() { self.hide(); }, 2000);
                }
            }, 1500);
        },

        hide() {
            const overlay = document.getElementById('ldRegistration');
            if (overlay) overlay.classList.add('hidden');
            clearInterval(this.interval);
        }
    },

    // ==========================================
    // 3. LOGIN (Pulsing Logo)
    // ==========================================
    login: {
        statuses: [
            { main: 'Verifying credentials...', sub: '+251 9XX XXX XXX' },
            { main: 'Checking subscription...', sub: 'Premium access confirmed' },
            { main: 'Loading 16 courses...', sub: 'Fetching worksheets & past exams' },
            { main: 'Welcome back!', sub: 'Opening dashboard...' }
        ],
        current: 0,
        interval: null,

        show() {
            const overlay = document.getElementById('ldLogin');
            if (!overlay) return;
            overlay.classList.remove('hidden');
            this.current = 0;
            this.updateStatus(0);
            this.startAutoAdvance();
        },

        updateStatus(index) {
            const main = document.getElementById('ldLoginMain');
            const sub = document.getElementById('ldLoginSub');
            if (!main) return;
            main.style.opacity = '0';
            setTimeout(function() {
                main.textContent = UNIYO_LOADER.login.statuses[index].main;
                if (sub) sub.textContent = UNIYO_LOADER.login.statuses[index].sub;
                main.style.opacity = '1';
            }, 200);
            this.current = index;
        },

        startAutoAdvance() {
            const self = this;
            clearInterval(this.interval);
            this.interval = setInterval(function() {
                if (self.current < self.statuses.length - 1) {
                    self.updateStatus(self.current + 1);
                } else {
                    clearInterval(self.interval);
                    setTimeout(function() { self.hide(); }, 1000);
                }
            }, 1500);
        },

        hide() {
            const overlay = document.getElementById('ldLogin');
            if (overlay) overlay.classList.add('hidden');
            clearInterval(this.interval);
        }
    },

    // ==========================================
    // 4. VIP CELEBRATION
    // ==========================================
    vip: {
        steps: [
            { main: 'Checking eligibility...', sub: 'Minimum score: 70%', ticket: false },
            { main: 'Verifying premium access...', sub: 'Subscription active', ticket: false },
            { main: 'Generating entry ticket...', sub: 'Week 12 Competition', ticket: false },
            { main: "You're in! 🎉", sub: 'Competition starts Monday', ticket: true }
        ],
        current: 0,
        interval: null,

        show() {
            const overlay = document.getElementById('ldVip');
            if (!overlay) return;
            overlay.classList.remove('hidden');
            this.current = 0;
            const ticket = document.getElementById('ldVipTicket');
            if (ticket) ticket.style.opacity = '0';
            this.updateStep(0);
            this.startAutoAdvance();
        },

        updateStep(index) {
            const main = document.getElementById('ldVipMain');
            const sub = document.getElementById('ldVipSub');
            const ticket = document.getElementById('ldVipTicket');
            if (!main) return;
            main.style.opacity = '0';
            setTimeout(function() {
                main.textContent = UNIYO_LOADER.vip.steps[index].main;
                if (sub) sub.textContent = UNIYO_LOADER.vip.steps[index].sub;
                main.style.opacity = '1';
                if (ticket) ticket.style.opacity = UNIYO_LOADER.vip.steps[index].ticket ? '1' : '0';
            }, 200);
            this.current = index;
        },

        startAutoAdvance() {
            const self = this;
            clearInterval(this.interval);
            this.interval = setInterval(function() {
                if (self.current < self.steps.length - 1) {
                    self.updateStep(self.current + 1);
                } else {
                    clearInterval(self.interval);
                    setTimeout(function() { self.hide(); }, 2000);
                }
            }, 1400);
        },

        hide() {
            const overlay = document.getElementById('ldVip');
            if (overlay) overlay.classList.add('hidden');
            clearInterval(this.interval);
        }
    },

    // ==========================================
    // 5. PAYMENT MODAL
    // ==========================================
    payment: {
        show() {
            const modal = document.getElementById('ldPayment');
            if (!modal) return;
            modal.classList.remove('hidden');
            this.reset();
        },

        reset() {
            const input = document.getElementById('ldPaymentInput');
            const main = document.getElementById('ldPaymentMain');
            const sub = document.getElementById('ldPaymentSub');
            const progress = document.getElementById('ldPaymentProgress');
            const btnRow = document.getElementById('ldPaymentBtnRow');
            const confirmBtn = document.getElementById('ldPaymentConfirmBtn');

            if (input) { input.value = ''; input.classList.remove('error', 'success'); }
            if (main) main.textContent = 'Type your transaction number above';
            if (sub) sub.textContent = '300 ETB • Telebirr';
            if (progress) progress.style.width = '0%';
            if (btnRow) btnRow.style.display = 'flex';
            if (confirmBtn) confirmBtn.disabled = true;
        },

        onInput() {
            const input = document.getElementById('ldPaymentInput');
            const confirmBtn = document.getElementById('ldPaymentConfirmBtn');
            const main = document.getElementById('ldPaymentMain');
            if (!input) return;
            input.value = input.value.toUpperCase();
            if (confirmBtn) confirmBtn.disabled = input.value.length < 5;
            if (main && input.value.length >= 5) {
                main.textContent = 'Is this transaction number correct?';
            }
            input.classList.remove('error', 'success');
        },

        confirm() {
            const input = document.getElementById('ldPaymentInput');
            const main = document.getElementById('ldPaymentMain');
            const sub = document.getElementById('ldPaymentSub');
            const progress = document.getElementById('ldPaymentProgress');
            const btnRow = document.getElementById('ldPaymentBtnRow');

            if (!input || input.value.length < 5) {
                if (input) input.classList.add('error');
                return;
            }

            input.classList.add('success');
            if (btnRow) btnRow.style.display = 'none';
            if (main) main.textContent = 'Verifying with Telebirr...';
            if (sub) sub.textContent = 'Matching: ' + input.value;
            if (progress) progress.style.width = '30%';

            setTimeout(function() {
                if (main) main.textContent = 'Transaction found!';
                if (sub) sub.textContent = input.value + ' • 300 ETB • Confirmed';
                if (progress) progress.style.width = '70%';
            }, 1500);

            setTimeout(function() {
                if (main) main.textContent = 'Submitting for admin approval...';
                if (sub) sub.textContent = 'Sending notification to @UNIYO_Support';
                if (progress) progress.style.width = '90%';
            }, 3000);

            setTimeout(function() {
                if (main) main.textContent = '✅ Submitted successfully!';
                if (sub) sub.textContent = "You'll get access once approved";
                if (progress) progress.style.width = '100%';
            }, 4500);

            setTimeout(function() { UNIYO_LOADER.payment.hide(); }, 6000);
        },

        hide() {
            const modal = document.getElementById('ldPayment');
            if (modal) modal.classList.add('hidden');
        }
    },

    // ==========================================
    // 6. CERTIFICATE MODAL
    // ==========================================
    certificate: {
        steps: [
            { item: 1, main: 'Rendering gold badge...', sub: 'VIP Gold #F59E0B', progress: 20 },
            { item: 2, main: 'Applying watermark...', sub: 'Anti-tamper protection', progress: 40 },
            { item: 3, main: 'Embedding student name...', sub: 'Abebe Kebede • Natural Science', progress: 60 },
            { item: 4, main: 'Generating QR code...', sub: 'Verification URI attached', progress: 80 },
            { item: 5, main: 'Finalizing PDF...', sub: 'Preparing download...', progress: 100 }
        ],
        current: 0,

        show() {
            const modal = document.getElementById('ldCertificate');
            if (!modal) return;
            modal.classList.remove('hidden');
            this.reset();
            this.startGeneration();
        },

        reset() {
            for (let i = 1; i <= 5; i++) {
                const item = document.getElementById('ldCertItem' + i);
                if (item) {
                    item.classList.remove('active', 'done');
                    const icon = item.querySelector('.ld-check-icon');
                    if (icon) icon.textContent = '•';
                }
            }
            const progress = document.getElementById('ldCertProgress');
            const main = document.getElementById('ldCertMain');
            const sub = document.getElementById('ldCertSub');
            if (progress) progress.style.width = '0%';
            if (main) main.textContent = 'Starting...';
            if (sub) sub.textContent = 'staff.py generator';
            this.current = 0;
        },

        startGeneration() {
            const self = this;
            const runStep = function() {
                if (self.current > 0) {
                    const prevItem = document.getElementById('ldCertItem' + self.steps[self.current - 1].item);
                    if (prevItem) {
                        prevItem.classList.remove('active');
                        prevItem.classList.add('done');
                        const icon = prevItem.querySelector('.ld-check-icon');
                        if (icon) icon.textContent = '✓';
                    }
                }

                if (self.current < self.steps.length) {
                    const step = self.steps[self.current];
                    const item = document.getElementById('ldCertItem' + step.item);
                    if (item) {
                        item.classList.add('active');
                        const icon = item.querySelector('.ld-check-icon');
                        if (icon) icon.textContent = '⟳';
                    }
                    const main = document.getElementById('ldCertMain');
                    const sub = document.getElementById('ldCertSub');
                    const progress = document.getElementById('ldCertProgress');
                    if (main) main.textContent = step.main;
                    if (sub) sub.textContent = step.sub;
                    if (progress) progress.style.width = step.progress + '%';
                    self.current++;
                    setTimeout(runStep, 1200);
                } else {
                    setTimeout(function() {
                        const main = document.getElementById('ldCertMain');
                        const sub = document.getElementById('ldCertSub');
                        if (main) main.textContent = '✅ Certificate Ready!';
                        if (sub) sub.textContent = 'Opening document viewer...';
                        setTimeout(function() { self.hide(); }, 1500);
                    }, 500);
                }
            };
            runStep();
        },

        hide() {
            const modal = document.getElementById('ldCertificate');
            if (modal) modal.classList.add('hidden');
        }
    },

    // ==========================================
    // 7. EXAM DOWNLOAD
    // ==========================================
    examDownload: {
        progress: 0,
        interval: null,

        show() {
            const overlay = document.getElementById('ldDownload');
            if (!overlay) return;
            overlay.classList.remove('hidden');
            this.progress = 0;
            this.updateProgress(0);
            const status = document.getElementById('ldDownloadStatus');
            if (status) status.textContent = 'Starting download...';
            this.start();
        },

        updateProgress(progress) {
            const pct = document.getElementById('ldDownloadPercentage');
            const fill = document.getElementById('ldDownloadProgress');
            const bytes = document.getElementById('ldDownloadBytes');
            const totalSize = 12.4;
            const downloaded = ((progress / 100) * totalSize).toFixed(1);
            if (pct) pct.textContent = progress + '%';
            if (fill) fill.style.width = progress + '%';
            if (bytes) bytes.textContent = downloaded + ' MB / ' + totalSize + ' MB';
        },

        start() {
            const self = this;
            clearInterval(this.interval);
            this.interval = setInterval(function() {
                self.progress += Math.floor(Math.random() * 15) + 5;
                if (self.progress >= 100) {
                    self.progress = 100;
                    clearInterval(self.interval);
                    const status = document.getElementById('ldDownloadStatus');
                    if (status) status.textContent = 'Download complete! Opening viewer...';
                    setTimeout(function() { self.hide(); }, 1500);
                } else if (self.progress > 60) {
                    const status = document.getElementById('ldDownloadStatus');
                    if (status) status.textContent = 'Optimizing for mobile...';
                } else if (self.progress > 30) {
                    const status = document.getElementById('ldDownloadStatus');
                    if (status) status.textContent = 'Downloading PDF...';
                }
                self.updateProgress(self.progress);
            }, 400);
        },

        hide() {
            const overlay = document.getElementById('ldDownload');
            if (overlay) overlay.classList.add('hidden');
            clearInterval(this.interval);
        }
    },

    // ==========================================
    // 8. OFFLINE SYNC TOAST
    // ==========================================
    offlineSync: {
        steps: [
            { title: 'Syncing 1 of 3...', sub: 'Psych1011 • Score: 75%', queue: '3 LEFT' },
            { title: 'Syncing 2 of 3...', sub: 'Hist1012 • Score: 85%', queue: '2 LEFT' },
            { title: 'Syncing 3 of 3...', sub: 'GeES1011 • Score: 90%', queue: '1 LEFT' },
            { title: 'All synced! ✅', sub: 'Back online', queue: 'DONE' }
        ],
        current: 0,

        show() {
            const toast = document.getElementById('ldSyncToast');
            if (!toast) return;
            toast.classList.add('visible');
            toast.classList.remove('success');
            this.current = 0;
            this.updateSync(0);
            this.startAutoSync();
        },

        updateSync(index) {
            const title = document.getElementById('ldSyncTitle');
            const sub = document.getElementById('ldSyncSub');
            const queue = document.getElementById('ldSyncQueue');
            const toast = document.getElementById('ldSyncToast');
            if (title) title.textContent = this.steps[index].title;
            if (sub) sub.textContent = this.steps[index].sub;
            if (queue) queue.textContent = this.steps[index].queue;
            if (index === this.steps.length - 1 && toast) toast.classList.add('success');
        },

        startAutoSync() {
            const self = this;
            const interval = setInterval(function() {
                self.current++;
                if (self.current < self.steps.length) {
                    self.updateSync(self.current);
                } else {
                    clearInterval(interval);
                    setTimeout(function() {
                        const toast = document.getElementById('ldSyncToast');
                        if (toast) toast.classList.remove('visible');
                    }, 2000);
                }
            }, 1500);
        }
    },

    // ==========================================
    // 9. PROFILE UPDATE BUTTON
    // ==========================================
    profileUpdate: {
        start(buttonId) {
            const btn = document.getElementById(buttonId) || document.getElementById('ldSaveBtn');
            if (!btn) return;
            const icon = btn.querySelector('.ld-btn-icon') || btn.querySelector('#ldBtnIcon');
            const text = btn.querySelector('.ld-btn-text') || btn.querySelector('#ldBtnText');

            btn.disabled = true;
            if (icon) icon.innerHTML = '<span class="ld-btn-spinner"></span>';
            if (text) text.textContent = 'Saving...';

            setTimeout(function() {
                if (text) text.textContent = 'Updating...';
            }, 800);

            setTimeout(function() {
                if (icon) icon.innerHTML = '✅';
                if (text) text.textContent = 'Saved!';
                btn.classList.add('ld-saved');
                setTimeout(function() {
                    btn.disabled = false;
                    if (icon) icon.innerHTML = '💾';
                    if (text) text.textContent = 'Save Changes';
                    btn.classList.remove('ld-saved');
                }, 2000);
            }, 1800);
        }
    },

    // ==========================================
    // 10. SESSION EXPIRY
    // ==========================================
    sessionExpiry: {
        value: 5,
        interval: null,
        ringCircumference: 2 * Math.PI * 36,

        show() {
            const overlay = document.getElementById('ldSession');
            if (!overlay) return;
            overlay.classList.remove('hidden');
            this.value = 5;
            this.updateCountdown();
            this.startCountdown();
        },

        updateCountdown() {
            const countdown = document.getElementById('ldSessionCountdown');
            const ring = document.getElementById('ldSessionRing');
            if (countdown) countdown.textContent = this.value;
            if (ring) {
                const progress = (this.value / 5) * this.ringCircumference;
                ring.style.strokeDashoffset = this.ringCircumference - progress;
            }
        },

        startCountdown() {
            const self = this;
            clearInterval(this.interval);
            this.interval = setInterval(function() {
                self.value--;
                const msg = document.getElementById('ldSessionMsg');
                if (self.value > 0) {
                    self.updateCountdown();
                    if (msg) msg.textContent = 'Redirecting to login in ' + self.value + ' seconds...';
                } else {
                    self.updateCountdown();
                    const countdown = document.getElementById('ldSessionCountdown');
                    if (countdown) countdown.textContent = '0';
                    if (msg) msg.textContent = 'Redirecting now...';
                    clearInterval(self.interval);
                    setTimeout(function() {
                        self.hide();
                        // Uncomment to redirect:
                        // window.location.href = '/student/login';
                    }, 800);
                }
            }, 1000);
        },

        hide() {
            const overlay = document.getElementById('ldSession');
            if (overlay) overlay.classList.add('hidden');
            clearInterval(this.interval);
        }
    }
};

// Global access
window.UNIYO_LOADER = UNIYO_LOADER;
