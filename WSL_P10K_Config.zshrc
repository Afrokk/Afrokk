# ────────────────────────────  POWERLEVEL10K INSTANT PROMPT  ────────────────────────────
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ─────────────────────────────  OH-MY-ZSH CORE SETTINGS  ────────────────────────────────
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
  git
  zsh-autocomplete
  zsh-autosuggestions
  zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

# ─────────────────────────────  POWERLEVEL10K SETTINGS  ────────────────────────────────
# If you've never run p10k configure before, launch it once.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ─────────────────────────────  ZSH-SYNTAX-HIGHLIGHTING  ───────────────────────────────
# Extra highlighters & patterns (copied from your Mac)
ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets pattern cursor root line)
ZSH_HIGHLIGHT_PATTERNS=('rm -rf *' 'fg=white,bold,bg=red')

# ─────────────────────────────  LS COLORS (same as Mac)  ───────────────────────────────
export LS_COLORS="rs=0:no=00:mi=00:mh=00:ln=01;36:or=01;31:di=01;34:ow=04;01;34:st=34:tw=04;34:pi=01;33:so=01;33:do=01;33:bd=01;33:cd=01;33:su=01;35:sg=01;35:ca=01;35:ex=01;32:"

# ─────────────────────────────  CONDA (WSL path!)  ─────────────────────────────────────
# Adapt this to wherever you installed Miniconda in WSL.
__conda_setup="$('$HOME/miniconda3/bin/conda' 'shell.zsh' 'hook' 2>/dev/null)"
if [ $? -eq 0 ]; then
  eval "$__conda_setup"
else
  if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
# source "$HOME/miniconda3/etc/profile.d/conda.sh"  # commented out by conda initialize
  else
# export PATH="$HOME/miniconda3/bin:$PATH"  # commented out by conda initialize
  fi
fi
unset __conda_setup

# ─────────────────────────────  NVM  ───────────────────────────────────────────────────
export NVM_DIR="$HOME/.nvm"
[[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
[[ -s "$NVM_DIR/bash_completion" ]] && source "$NVM_DIR/bash_completion"

# ─────────────────────────────  MISC  ──────────────────────────────────────────────────
# Case-sensitive completion off; enable “magic” & autosuggestions tweaks, etc.
# Uncomment what you need (examples):
# CASE_SENSITIVE="true"
# ENABLE_CORRECTION="true"
# DISABLE_LS_COLORS="true"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/afrokk/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/afrokk/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/afrokk/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/afrokk/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# ssh agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

