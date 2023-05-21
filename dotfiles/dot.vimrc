" ~/.vimrc


"
" Configure the basics
"


" Lay out Spaces and Tabs

:set softtabstop=4 shiftwidth=4 expandtab
:autocmd FileType cpp  set softtabstop=8 shiftwidth=8 noexpandtab
:autocmd FileType cpp  set softtabstop=4 shiftwidth=4 expandtab


" Choose colors

:set background=dark
:set background=light
:syntax off
:syntax on  " such as for ':set syntax=.bash'


" Don't redefine the conventional Mouse Clicks

:set mouse=a
:set mouse=  " Option+LeftClick moves Cursor


" Say to more show what's going on
" Choose ':set showcmd' and ':set ruler' explicitly, apart from ':set ttyfast'
" Shrug off macOS Vim leaving 'ttyfast' out of ':set'

:set cursorline
:set nocursorline
:autocmd InsertEnter * set cul  " styles the Cursor Line to show Insert/ Replace/ not
:autocmd InsertLeave * set nocul

:set noshowmode
:set showmode  " says '-- INSERT --' in bottom line while you remain in Insert Mode

:set noshowcmd
:set showcmd  " shows the first few Keys pressed while waiting for more

:set noruler
:set ruler  " shows the Line & Column Numbers of the Cursor

:set invnumber
:set number
:set nonumber  " doesn't show a Line Number to the left of each Line

:set noignorecase
:set invignorecase
:set ignorecase  " ignores Upper/ Lower Case in Searches

:set wrap
:set nowrap  " secretly hides any text that exists beyond the right margin

:set nohlsearch
:set hlsearch  " lights up all matches till you :noh, like with \ Esc

:highlight RedLight ctermbg=red
:call matchadd('RedLight', '\s\+$')  " lights up Tabs and Spaces at end-of-line

:startinsert
:stopinsert  " starts in Normal View Mode, not in Insert Mode


"
" Define more Key Chord Sequences without redefining conventional Sequences
"
" N-NoRe-Map = Map only for Normal (View) Mode and don't Recurse through other maps
"


" Take macOS ⌥← Option Left-Arrow as alias of Vim ⇧B
" Take macOS ⌥→ Option Right-Arrow take as alias of Vim ⇧W
:nnoremap <Esc>b B
:nnoremap <Esc>f W


" \ \  => Gracefully do nothing
:nnoremap <BSlash><BSlash> :<return>

" \ Esc  => Cancel the :set hlsearch highlighting of all search hits on screen
:nnoremap <BSlash><Esc> :noh<return>

" \ ⇧I  => Toggle ignoring case in searches, but depends on :set nosmartcase
:nnoremap <BSlash>i :set invignorecase<return>

" \ N  => Toggle line numbers
:nnoremap <BSlash>n :set invnumber<return>

" \ W  => Delete the trailing whitespace from each line (not yet from file)
:nnoremap <BSlash>w :call RStripEachLine()<return>
:function! RStripEachLine()
    let with_line = line(".")
    let with_col = col(".")
    %s/\s\+$//e
    call cursor(with_line, with_col)
endfun

" ⇧Z ⇧E  => Discard changes and reload
:nnoremap ZE :e!<return>
" ⇧Z ⇧Q => Quit Without Saving
" ⇧Z ⇧W  => save changes
:nnoremap ZW :w<return>
" ⇧Z ⇧Z => Save Then Quit


" posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.vimrc
" copied from:  git clone https://github.com/pelavarre/byoverbs.git
