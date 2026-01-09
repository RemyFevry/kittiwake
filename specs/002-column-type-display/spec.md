# Feature Specification: Column Type Display and Quick Filter

**Feature Branch**: `002-column-type-display`  
**Created**: 2026-01-09  
**Status**: Draft  
**Input**: User description: "update the specs so that its possible to filter on clicking/selecting a column name, also we should see the type of each column, also each type should have a different color"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visual Column Type Identification (Priority: P1)

As a data analyst exploring a new dataset, I want to immediately see what type of data each column contains (numbers, text, dates, etc.) so I can quickly understand the dataset structure without reading documentation or inspecting values.

**Why this priority**: This is the foundation for data exploration. Users need to understand data types before performing any meaningful analysis. Without clear type indicators, users waste time clicking through columns or examining sample values to determine data types.

**Independent Test**: Can be fully tested by loading any dataset and visually inspecting column headers. Delivers immediate value by eliminating the need to inspect data to determine column types.

**Acceptance Scenarios**:

1. **Given** a dataset is loaded with columns of different types, **When** I view the table, **Then** each column header displays a visual indicator (color or symbol) showing its data type
2. **Given** I'm viewing column headers, **When** I look at numeric columns, **Then** they are displayed in one distinct color
3. **Given** I'm viewing column headers, **When** I look at text/string columns, **Then** they are displayed in a different distinct color from numeric columns
4. **Given** I'm viewing column headers, **When** I look at date/time columns, **Then** they are displayed in a distinct color different from numeric and text columns
5. **Given** I'm viewing column headers, **When** I look at boolean columns, **Then** they are displayed in a distinct color
6. **Given** column headers with type colors, **When** I view the color legend or help, **Then** I can see what each color represents

---

### User Story 2 - Quick Filter from Column Header (Priority: P2)

As a data analyst, I want to create filters by clicking directly on column headers so I can quickly filter data without opening separate modal dialogs and manually selecting columns from dropdowns.

**Why this priority**: This dramatically speeds up the most common operation in data exploration - filtering. The current Ctrl+F workflow requires opening a modal, selecting a column from a dropdown, choosing an operator, and entering a value. Direct column clicking reduces this to 2 steps.

**Independent Test**: Can be tested by clicking on any column header and verifying that a filter interface appears. Delivers value by providing a faster path to filtering that complements the existing Ctrl+F workflow.

**Acceptance Scenarios**:

1. **Given** I'm viewing a dataset table, **When** I click on a column header, **Then** a filter interface appears for that specific column
2. **Given** I clicked on a numeric column header, **When** the filter interface appears, **Then** it shows numeric operators (>, <, >=, <=, =, !=) and accepts numeric input
3. **Given** I clicked on a text/string column header, **When** the filter interface appears, **Then** it shows text operators (equals, not equals, contains) and accepts text input
4. **Given** I clicked on a date column header, **When** the filter interface appears, **Then** it shows date operators (before, after, between) and accepts date input
5. **Given** I clicked on a boolean column header, **When** the filter interface appears, **Then** it shows options to filter by true/false values
6. **Given** I'm in the column header filter interface, **When** I submit a filter, **Then** the filter is created as a queued operation (in lazy mode) or executed immediately (in eager mode)
7. **Given** I'm in the column header filter interface, **When** I cancel or press Escape, **Then** the filter interface closes without creating an operation

---

### User Story 3 - Column Type Display with Icon (Priority: P3)

As a user working with complex datasets, I want to see both a color AND an icon/symbol for each column type so I can identify types even if I have color blindness or work in low-contrast environments.

**Why this priority**: Accessibility enhancement. While color-coding is the primary visual indicator (P1), adding icons ensures the feature works for users with color vision deficiencies and in various display conditions.

**Independent Test**: Can be tested by viewing column headers and verifying that both color and icon are present. Delivers value by making the feature accessible to all users regardless of visual capabilities.

**Acceptance Scenarios**:

1. **Given** a dataset is loaded, **When** I view column headers, **Then** each header shows both a color and an icon representing the data type
2. **Given** I'm viewing column headers, **When** I look at a numeric column, **Then** it shows a numeric icon (e.g., "#", "123", or similar)
3. **Given** I'm viewing column headers, **When** I look at a text column, **Then** it shows a text icon (e.g., "T", "abc", or similar)
4. **Given** I'm viewing column headers, **When** I look at a date column, **Then** it shows a date icon (e.g., calendar symbol)
5. **Given** I'm viewing column headers, **When** I look at a boolean column, **Then** it shows a boolean icon (e.g., checkbox, true/false symbol)

---

### Edge Cases

- What happens when a column contains mixed types or null values? Which type takes precedence for color/icon display?
- How does the column header filter interact with existing queued filters? Does it replace, append, or warn?
- What happens if the column type is unknown or unsupported (e.g., complex nested objects)?
- How does the quick filter UI handle very long column names? Does it truncate or wrap?
- What happens if user clicks on a column header that is already part of an active filter?
- How does the color scheme work if there are more data types than colors defined?
- What happens if the user rapidly clicks multiple column headers? Does each open a separate filter UI or does it replace the current one?

## Requirements *(mandatory)*

### Functional Requirements

#### Visual Type Display

- **FR-001**: System MUST display each column header with a distinct color based on its data type
- **FR-002**: System MUST support at least these data type categories: numeric (integers, floats), text/string, date/time, boolean, and unknown/mixed
- **FR-003**: System MUST use colors that provide sufficient contrast against the background for readability
- **FR-004**: System MUST provide a visual legend or reference showing which color represents which data type (accessible via help overlay or tooltip)
- **FR-005**: System MUST display an icon or symbol alongside the color for each column type to support accessibility

#### Quick Filter Interaction

- **FR-006**: System MUST allow users to trigger a filter interface by clicking on any column header
- **FR-007**: System MUST display a context-appropriate filter interface based on the clicked column's data type
- **FR-008**: System MUST show numeric filter operators (>, <, >=, <=, =, !=) when filtering numeric columns
- **FR-009**: System MUST show text filter operators (equals, not equals, contains) when filtering text columns
- **FR-010**: System MUST show date filter operators (before, after, between, equals) when filtering date columns
- **FR-011**: System MUST show boolean filter options (true, false, null) when filtering boolean columns
- **FR-012**: System MUST create operations using the same operation model as the existing Ctrl+F filter workflow
- **FR-013**: System MUST respect the current execution mode (lazy vs eager) when creating filters from column headers
- **FR-014**: System MUST allow users to cancel the quick filter interface without creating an operation
- **FR-015**: System MUST close the quick filter interface automatically after successful filter creation

#### Integration with Existing Features

- **FR-016**: System MUST maintain backward compatibility with existing Ctrl+F filter workflow
- **FR-017**: System MUST maintain backward compatibility with existing Ctrl+H search workflow
- **FR-018**: Column header filters MUST appear in the operations sidebar with the same state indicators (⏳, ✓, ✗) as other operations
- **FR-019**: Column header filters MUST be undoable/redoable using Ctrl+Z/Ctrl+Shift+Z
- **FR-020**: System MUST update the operations sidebar immediately when a column header filter is created
- **FR-021**: System MUST display inline validation errors when filter values don't match expected type (e.g., text in numeric field, malformed date) and prevent operation submission until valid

### Key Entities

- **Column Header**: Represents the header of a data table column, including its name, data type, color indicator, icon, and click handler for quick filtering
- **Data Type**: Represents the classification of data in a column (numeric, text, date, boolean, unknown), determines visual styling and available filter operators
- **Quick Filter Interface**: A contextual UI component that appears when clicking a column header, pre-populated with the selected column and showing type-appropriate operators
- **Type Color Scheme**: Mapping between data types and their corresponding visual colors and icons

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify the data type of any column in under 2 seconds by visual inspection alone
- **SC-002**: Users can create a filter for a specific column in under 5 seconds using the column header click method (compared to 10-15 seconds with current Ctrl+F workflow)
- **SC-003**: 100% of data type categories (numeric, text, date, boolean, unknown) are distinguishable by color AND icon
- **SC-004**: Quick filter workflow reduces the number of steps to create a filter by at least 50% (from 5 steps to 2-3 steps)
- **SC-005**: Color contrast between type indicators and background meets WCAG 2.1 Level AA standards (contrast ratio of at least 4.5:1)
- **SC-006**: Users with color blindness can successfully identify column types using icon indicators alone
- **SC-007**: 90% of users can successfully create a column filter on their first attempt without consulting help documentation

### User Experience Goals

- **UX-001**: Visual type indicators are immediately noticeable but not distracting from data content
- **UX-002**: Quick filter interaction feels natural and discoverable (users intuitively try clicking column headers)
- **UX-003**: Filter creation workflow from column headers feels faster and more direct than modal-based approach
- **UX-004**: Type color scheme is consistent across all views and operations
