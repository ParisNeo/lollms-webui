#!/bin/bash

# Clone the repository to a tmp folder
REPO_URL="https://github.com/ParisNeo/PyAIPersonality.git"
TMP_FOLDER=$(mktemp -d)
git clone "$REPO_URL" "$TMP_FOLDER"

# List the available languages and prompt user to select one
LANGUAGES_FOLDER="$TMP_FOLDER/personalities_zoo"
LANGUAGE_INDEX=0
for d in "$LANGUAGES_FOLDER"/*; do
  LANGUAGE_INDEX=$((LANGUAGE_INDEX+1))
  LANGUAGES[$LANGUAGE_INDEX]=$(basename "$d")
  echo "$LANGUAGE_INDEX. ${LANGUAGES[$LANGUAGE_INDEX]}"
done
read -p "Enter the number of the desired language: " SELECTED_LANGUAGE
LANGUAGE_FOLDER="$LANGUAGES_FOLDER/${LANGUAGES[$SELECTED_LANGUAGE]}"

# List the available categories and prompt user to select one
CATEGORIES_FOLDER="$LANGUAGE_FOLDER"
CATEGORY_INDEX=0
for d in "$CATEGORIES_FOLDER"/*; do
  CATEGORY_INDEX=$((CATEGORY_INDEX+1))
  CATEGORIES[$CATEGORY_INDEX]=$(basename "$d")
  echo "$CATEGORY_INDEX. ${CATEGORIES[$CATEGORY_INDEX]}"
done
read -p "Enter the number of the desired category: " SELECTED_CATEGORY
CATEGORY_FOLDER="$CATEGORIES_FOLDER/${CATEGORIES[$SELECTED_CATEGORY]}"

# List the available personalities and prompt user to select one
PERSONALITIES_FOLDER="$CATEGORY_FOLDER"
PERSONALITY_INDEX=0
for d in "$PERSONALITIES_FOLDER"/*; do
  PERSONALITY_INDEX=$((PERSONALITY_INDEX+1))
  PERSONALITIES[$PERSONALITY_INDEX]=$(basename "$d")
  echo "$PERSONALITY_INDEX. ${PERSONALITIES[$PERSONALITY_INDEX]}"
done
read -p "Enter the number of the desired personality: " SELECTED_PERSONALITY
PERSONALITY_FOLDER="$PERSONALITIES_FOLDER/${PERSONALITIES[$SELECTED_PERSONALITY]}"

# Copy the selected personality folder to personalities/language/category folder
OUTPUT_FOLDER="$(pwd)/personalities/${LANGUAGES[$SELECTED_LANGUAGE]}/${CATEGORIES[$SELECTED_CATEGORY]}/${PERSONALITIES[$SELECTED_PERSONALITY]}"
mkdir -p "$OUTPUT_FOLDER"
cp -r "$PERSONALITY_FOLDER/." "$OUTPUT_FOLDER"

# Cleaning
if [[ -d "./tmp" ]]; then
  echo "Cleaning tmp folder"
  rm -rf "./tmp"
fi

# Remove the tmp folder
rm -rf "$TMP_FOLDER"
