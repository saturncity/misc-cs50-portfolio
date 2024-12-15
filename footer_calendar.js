// footer_calendar.js
/*
   footer_calendar.js
   - Fetch availability from backend
   - Mark unavailable in red ("Unavailable"), beyond 90 days grey ("(Date too far in future)")
   - No bold/underline for months.
*/

(async function() {
    var calendarContainer = document.getElementById('calendar-container');

    async function fetchAvailabilityData() {
        try {
            let response = await fetch('/availability_data');
            if (!response.ok) throw new Error('Network response was not ok');
            let data = await response.json();
            return data;
        } catch (err) {
            console.error('Error fetching availability data:', err);
            return {};
        }
    }

    function getUTCDate() {
        return new Date();
    }

    async function generateCalendars() {
        var availabilityData = await fetchAvailabilityData();
        var todayUTC = getUTCDate();
        var endDate = new Date(Date.UTC(todayUTC.getUTCFullYear(), todayUTC.getUTCMonth(), todayUTC.getUTCDate()));
        endDate.setUTCDate(endDate.getUTCDate() + 89);

        calendarContainer.innerHTML = '';
        var startYear = todayUTC.getUTCFullYear();
        var startMonth = todayUTC.getUTCMonth();

        for (var m = 0; m < 4; m++) {
            var monthDate = new Date(Date.UTC(startYear, startMonth + m, 1));
            generateCalendarMonth(monthDate, todayUTC, endDate, availabilityData);
        }
    }

    function generateCalendarMonth(monthDate, todayUTC, endDate, availabilityData) {
        var year = monthDate.getUTCFullYear();
        var month = monthDate.getUTCMonth();
        var monthName = monthDate.toLocaleString('en-GB', { month: 'long', timeZone: 'UTC' });

        var daysInMonth = new Date(Date.UTC(year, month+1, 0)).getUTCDate();
        var firstDay = new Date(Date.UTC(year, month, 1)).getUTCDay();
        var dayMap = [7,1,2,3,4,5,6];
        var startIndex = dayMap[firstDay];

        var monthDiv = document.createElement('div');
        monthDiv.className = 'calendar-month';

        var header = document.createElement('div');
        header.className = 'calendar-header';
        header.textContent = monthName + " " + year;
        monthDiv.appendChild(header);

        var daysRow = document.createElement('div');
        daysRow.className = 'calendar-grid';
        var daysLabel = ['M','T','W','T','F','S','S','U'];
        daysLabel.forEach(function(d) {
            var lbl = document.createElement('div');
            lbl.textContent = d;
            daysRow.appendChild(lbl);
        });

        var cells = [];
        for (var i = 0; i < 42; i++) {
            var cell = document.createElement('div');
            cells.push(cell);
        }

        for (var d = 1; d <= daysInMonth; d++) {
            var dateObj = new Date(Date.UTC(year, month, d));
            var index = (d - 1) + startIndex;
            var ymd = year + '-' + String(month+1).padStart(2,'0') + '-' + String(d).padStart(2,'0');

            cells[index].textContent = d;

            if (dateObj > endDate) {
                cells[index].classList.add('grayed-out');
                cells[index].setAttribute('title', '(Date too far in future)');
            } else if (dateObj < todayUTC) {
                cells[index].classList.add('grayed-out');
            } else {
                if (availabilityData[ymd] === 'unavailable') {
                    cells[index].classList.add('unavailable');
                    cells[index].setAttribute('title', 'Unavailable');
                }
            }
        }

        cells.forEach(function(c) { daysRow.appendChild(c); });
        monthDiv.appendChild(daysRow);
        calendarContainer.appendChild(monthDiv);
    }

    await generateCalendars();
})();
