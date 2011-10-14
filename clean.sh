#!/bin/bash

HOME=`pwd`
TREE=tree ; export TREE

if [ "$(ls -A $HOME/$TREE)" ]; then
    rm -r $HOME/$TREE
    echo "Removed entire tree directory"
else
    echo "$HOME/$TREE does not exist (nothing to remove)"
fi

rm *.pyc
echo "Removed all compiled python files (.pyc)"

