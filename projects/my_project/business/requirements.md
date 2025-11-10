# Project Requirements

## Project Overview

**Name**: LocalNetChat

**Description**: A lightweight desktop/mobile chat application that operates entirely over a local network (LAN). It allows users to exchange text messages, broadcast status updates, and share files without requiring internet connectivity or external servers.

**Target Audience**: Small teams, classrooms, or any environment where users share a local network.

**Platforms**: Windows, macOS, Linux, Android, iOS



## User Stories

### User Identification

**ID**: US01

**Description**: As a user, I want to choose a unique display name so that others can identify me.

**Acceptance Criteria**:

- The app prompts for a username on first launch.

- Duplicate usernames are rejected with an error message.



### View Online Users

**ID**: US02

**Description**: As a user, I want to see a list of all currently online users along with their status.

**Acceptance Criteria**:

- The user list updates in real time as peers join/leave.

- Each entry shows the user’s display name and status (Online/Offline/Busy/Idle).



### Send & Receive Text Messages

**ID**: US03

**Description**: As a user, I want to send text messages to individual peers and receive them instantly.

**Acceptance Criteria**:

- Messages appear in a chat window with timestamp.

- The message is delivered within 200 ms on a typical LAN.



### Broadcast Status

**ID**: US04

**Description**: As a user, I want to set my status (Online/Busy/Idle) so that others can see my availability.

**Acceptance Criteria**:

- Status changes are reflected in the user list immediately.

- Status persists across application restarts.



### File Sharing

**ID**: US05

**Description**: As a user, I want to send files up to 50 MB to a peer, and receive them with progress feedback.

**Acceptance Criteria**:

- The file transfer completes within 5 seconds on a 100 Mbps LAN.

- The recipient can cancel the transfer mid‑stream.



### Chat History

**ID**: US06

**Description**: As a user, I want to view previous messages exchanged with a peer when I open the chat window.

**Acceptance Criteria**:

- Messages are persisted locally for 30 days.

- History is loaded instantly on opening a conversation.



### Cross‑Platform Consistency

**ID**: US07

**Description**: As a user, I want the same user experience on all supported platforms.

**Acceptance Criteria**:

- UI elements are responsive and use native controls where appropriate.

- Feature set is identical across platforms.



## Functional Requirements

- **FR01**: Automatically discover peers on the same subnet using mDNS/UDP broadcast.

- **FR02**: Encrypt all messages and file transfers using TLS 1.3 over a local socket.

- **FR03**: Queue outgoing messages and retry on transient network failures.

- **FR04**: Implement chunked transfer with checksum verification.

- **FR05**: Send periodic status updates to peers.

- **FR06**: Store user settings, chat history, and recent file transfer logs locally.



## Non-Functional Requirements

- **NFR01**: All UI interactions must be responsive (<200 ms).

- **NFR02**: Support up to 50 concurrent peers on a single subnet.

- **NFR03**: The application must recover from network interruptions without data loss.

- **NFR04**: Ensure confidentiality, integrity, and authenticity of all communications.

- **NFR05**: Interface should be intuitive for non‑technical users.

- **NFR06**: Comply with GDPR for local data handling.



## Business Rules

- **BR01**: All communications occur exclusively within the local subnet; no external IP or DNS resolution is permitted.

- **BR02**: Maximum file size for transfer is 50 MB.

- **BR03**: Usernames must be unique per subnet.

- **BR04**: Message history retention period is 30 days.

- **BR05**: The application must not require administrative privileges to run.



## Success Criteria

- **SC01**: All user stories are fully implemented and pass automated tests.

- **SC02**: Message latency on a 100 Mbps LAN is <200 ms.

- **SC03**: File transfer of 50 MB completes in <5 seconds on a 100 Mbps LAN.

- **SC04**: The application runs on all target platforms without crashes.

- **SC05**: Security audit confirms TLS 1.3 usage and no plaintext data leakage.
