#!/usr/bin/env bash

# Ensure that the huey package is on the python-path, in the event it hasn't
# been installed using pip.
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export PYTHONPATH="${SCRIPT_DIR}/:$PYTHONPATH"
export PATH="/opt/homebrew/bin/:$PATH"

if [[ $1 == 'reload' ]]; then
  echo "Updating and reloading huey mster service: com.j.osx.trailinghuey.plist"
  cp $SCRIPT_DIR/com.j.osx.otp_mailcheck.plist ~/Library/LaunchAgents/com.j.osx.otp_mailcheck.plist
  launchctl unload ~/Library/LaunchAgents/com.j.osx.otp_mailcheck.plist
  launchctl load ~/Library/LaunchAgents/com.j.osx.otp_mailcheck.plist

  # Run the consumer with 2 worker threads.
  export SHELL=/opt/homebrew/bin/bash
  source ~/.profile
  source ~/.bash_profile

  hname=$(hostname)

  if [[ ${hname} == 'MacBook-Air-16G.lan' ]]; then
    echo "Running on MacBook-Air-16G.lan, not pulling any git changes."
    #pyenv activate metrics
  else
    echo "Running on ${hname}, pulling new git changes and starting huey."
    #pyenv activate global
    #/usr/bin/env bash -l -c "cd ${SCRIPT_DIR}; huey_consumer.py master.huey -w4"
  fi
  cd ${SCRIPT_DIR}
  python check_email.py
fi