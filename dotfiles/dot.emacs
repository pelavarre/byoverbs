; ~/.emacs


;
; Configure Emacs
;


(setq-default indent-tabs-mode nil)  ; indent with Spaces not Tabs
(setq-default tab-width 4)  ; count out columns of C-x TAB S-LEFT/S-RIGHT

(when (fboundp 'global-superword-mode) (global-superword-mode 't))  ; accelerate M-f M-b

(column-number-mode)  ; show column number up from 0, not just line number up from 1


;
; Add keys (without redefining keys)
; (as dry run by M-x execute-extended-command, M-: eval-expression)
;


(global-set-key (kbd "C-c %") 'query-replace-regexp)  ; for when C-M-% unavailable
(global-set-key (kbd "C-c -") 'undo)  ; for when C-- alias of C-_ unavailable
(global-set-key (kbd "C-c F") 'isearch-toggle-regexp)
(global-set-key (kbd "C-c O") 'overwrite-mode)  ; aka toggle Insert
(global-set-key (kbd "C-c b") 'ibuffer)  ; for ? m Q I O multi-buffer replace
(global-set-key (kbd "C-c m") 'xterm-mouse-mode)  ; toggle between move and select
(global-set-key (kbd "C-c o") 'occur)
(global-set-key (kbd "C-c r") 'revert-buffer)
(global-set-key (kbd "C-c s") 'superword-mode)  ; toggle accelerate of M-f M-b
(global-set-key (kbd "C-c w") 'whitespace-cleanup)

(setq linum-format "%2d ")
(global-set-key (kbd "C-c n") 'linum-mode)  ; toggle line numbers
(when (fboundp 'display-line-numbers-mode)
    (global-set-key (kbd "C-c n") 'display-line-numbers-mode))

(global-set-key (kbd "C-c r")
    (lambda () (interactive) (revert-buffer 'ignoreAuto 'noConfirm)))


;; Def C-c | = M-h C-u 1 M-| = Mark-Paragraph Universal-Argument Shell-Command-On-Region

(global-set-key (kbd "C-c |") 'like-shell-command-on-region)
(defun like-shell-command-on-region ()
    (interactive)
    (unless (mark) (mark-paragraph))
    (setq string (read-from-minibuffer
        "Shell command on region: " nil nil nil (quote shell-command-history)))
    (shell-command-on-region (region-beginning) (region-end) string nil 'replace)
    )


;
; Say how to turn off enough of macOS Terminal to run Emacs well
;

; Press Esc or ⌃[ to mean Meta, or else toggle
;     macOS Terminal > Preferences > Profiles > Keyboard > Use Option as Meta Key

; Confirm ⌃H K ⌃⇧2 or ⌃H K ⌃Space comes out as C-@ or C-SPC
;     to mean 'set-mark-command, even though older macOS needed you to turn off
;         System Preferences > Keyboard > Input Sources >
;         Shortcuts > Select The Previous Input Source  ⌃Space


; posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.emacs
; copied from:  git clone https://github.com/pelavarre/byoverbs.git
