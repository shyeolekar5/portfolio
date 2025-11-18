# Voice-to-Trello: AI-Powered Task Capture

## Motivation & Problem Solved

In fast-paced environments, capturing new tasks quickly often requires breaking flow, opening apps, and typing. This automation eliminates that friction by allowing **hands-free task capture**.

Simply speak your task, and this workflow handles the rest:

1. **Transcription** (Voice to Text).

2. **Intelligent Categorization** (AI extracts Name, Due Date, Priority, etc.).

3. **Structured Card Creation** (Instant Trello Card).

This solution ensures that thoughts and actions are instantly documented and organized without interrupting your work.

## Workflow Architecture

The entire process runs through a four-step Zapier automation, connecting the audio source to your project management board.

| **Step** | **App** | **Event** | **Role in Workflow** |
| :--- | :--- | :--- | :--- |
| **1. Trigger** | Webhooks by Zapier | Catch Hook | Receives the incoming audio file URL from the recorder application. |
| **2. Action** | AssemblyAI | Transcribe | Downloads the audio file and converts the voice command into raw text. |
| **3. Action** | AI by Zapier | Analyze & Return Data | Processes the text using a custom prompt to extract structured task data. |
| **4. Action** | Trello | Create Card | Maps the structured data to a Trello card on the designated board/list. |

## AI Extraction Schema

The AI by Zapier step is carefully prompted to extract the following critical metadata from the transcribed voice command, ensuring the resulting Trello card is immediately actionable and sortable:

| **Field Name** | **Description** | **Format Example** |
| :--- | :--- | :--- |
| **Name (Title)** | The concise title for the Trello card (the main task). | "Book a trip to British Columbia" |
| **Due Date** | The target completion date for the task. | `YYYY-MM-DD` (e.g., 2023-12-25) |
| **Description** | Detailed context, sub-tasks, or notes. | Longer narrative text. |
| **Category** | High-level grouping for sorting (e.g., Work, Personal, Others). | Work |
| **Priority** | The urgency level used for labeling/sorting. | High, Medium, or Low (Default: Medium) |

## Features at a Glance

* **Hands-free Task Capture:** Use any device capable of sending an audio file URL to a webhook.

* **Automatic Transcription:** Powered by AssemblyAI for highly accurate speech-to-text.

* **Intelligent Organization:** AI categorizes text into structured data, eliminating manual tagging.

* **Instant Trello Integration:** Cards are created automatically with pre-populated fields (Name, Due Date, etc.).

## 🛠️ Setup & Configuration

For a detailed, step-by-step guide on configuring the Webhook URL, connecting your accounts, and setting up the AI output schema, please refer to the configuration file:

* **See `zapier_flow.md` for full implementation instructions.**

## Requirements

1. **Zapier:** Required for Webhooks and AI by Zapier actions.

2. **AssemblyAI Account:** Required for the transcription service.

3. **Trello Account:** With a target Board and List created (e.g., "AI tasks" board, "Inbox" list).

4. **Source App:** An application or custom script capable of sending an audio file URL via `POST` request to the Zapier Webhook.

## How to Deploy and Test

1. **Obtain Webhook URL:** Complete Step 1 of the Zap setup (see `zapier_flow.md`) to get your unique Zapier Webhook URL.

2. **Configure Source App:** Integrate the Webhook URL into your voice recording application.

3. **Run Test:** Record a command like, "Schedule a meeting with the client for next Tuesday and make sure the priority is high."

4. **Verify Trello:** The Trello card should appear in your designated list with the title, due date, and priority labels automatically applied by the AI.