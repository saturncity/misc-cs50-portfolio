document.addEventListener('DOMContentLoaded', async () => {
    const calendarContainer = document.getElementById('calendar-container');

    async function fetchAvailability() {
        const response = await fetch('/availability_data');
        return response.ok ? await response.json() : {};
    }

    function generateCalendars(availabilityData) {
        const today = new Date();
        const maxDate = new Date();
        maxDate.setDate(today.getDate() + 90);

        calendarContainer.innerHTML = ''; // Clear existing calendars

        for (let monthOffset = 0; monthOffset < 4; monthOffset++) {
            const currentMonth = new Date(today.getFullYear(), today.getMonth() + monthOffset, 1);
            calendarContainer.appendChild(generateMonthCalendar(currentMonth, availabilityData, today, maxDate));
        }
    }

    function generateMonthCalendar(date, availabilityData, today, maxDate) {
        const year = date.getFullYear();
        const month = date.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const monthDiv = document.createElement('div');
        monthDiv.className = 'calendar-month';

        const header = document.createElement('div');
        header.className = 'calendar-header';
        header.textContent = date.toLocaleString('en-GB', { month: 'long', year: 'numeric' });
        monthDiv.appendChild(header);

        const grid = document.createElement('div');
        grid.className = 'calendar-grid';

        // Add day labels (7 columns)
        ['M', 'T', 'W', 'T', 'F', 'S', 'S'].forEach(day => {
            const label = document.createElement('div');
            label.textContent = day;
            grid.appendChild(label);
        });

        // Add empty placeholders for alignment
        const firstDay = new Date(year, month, 1).getDay(); // 0 (Sun) to 6 (Sat)
        const startOffset = firstDay === 0 ? 6 : firstDay - 1; // Adjust to Monday-start
        for (let i = 0; i < startOffset; i++) {
            const spacer = document.createElement('div');
            spacer.className = 'empty'; // Placeholder for alignment
            grid.appendChild(spacer);
        }

        // Add day cells
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('div');
            const dateKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const currentDate = new Date(Date.UTC(year, month, day));

            cell.textContent = day;

            if (currentDate < today) {
                // Dates in the past
                cell.className = 'grayed-out';
            } else if (currentDate > maxDate) {
                // Dates beyond 90 days
                cell.className = 'grayed-out';
            } else if (availabilityData[dateKey] === 'unavailable') {
                // Unavailable dates with tooltip
                cell.className = 'unavailable';
                cell.setAttribute('title', 'Unavailable');
            }

            grid.appendChild(cell);
        }

        monthDiv.appendChild(grid);
        return monthDiv;
    }

    const availabilityData = await fetchAvailability();
    generateCalendars(availabilityData);
});
