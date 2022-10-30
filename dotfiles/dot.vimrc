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
:syntax on


" Configure the other basics

:set noshowmode
:set showmode  " says '-- INSERT --' in bottom line while you remain in Insert Mode

:set noshowcmd
:set showcmd  " shows the Key pressed with Option/Alt, while waiting for next Key

:set noruler
:set ruler  " shows the Line & Column Numbers of the Cursor

:set invnumber
:set number
:set nonumber  " doesn't show a Line Number to the left of each Line

:set noignorecase
:set invignorecase
:set ignorecase

:set wrap
:set nowrap

:set nohlsearch
:set hlsearch

:highlight RedLight ctermbg=red
:call matchadd('RedLight', '\s\+$')

:startinsert
:stopinsert  " start in Normal View Mode, not in Insert Mode


"
" Add keys, but duck around to avoid redefining keys
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

" \ M  => Mouse moves cursor
" \ ⇧M  => Mouse selects zigzags of chars to copy-paste
:nnoremap <BSlash>m :set mouse=a<return>
:nnoremap <BSlash>M :set mouse=<return>

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

" ⇧Z E  => Reload, if no changes waiting for save
:nnoremap Ze :e<return>
" ⇧Z ⇧E  => Discard changes and reload
:nnoremap ZE :e!<return>
" ⇧Z ⇧Q => Quit Without Saving
" ⇧Z ⇧W  => save changes
:nnoremap ZW :w<return>
" ⇧Z ⇧Z => Save Then Quit


" posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.vimrc
" copied from:  git clone https://github.com/pelavarre/byoverbs.git
