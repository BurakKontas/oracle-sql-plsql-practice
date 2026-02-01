# SQL Quiz Application

A desktop application for practicing SQL queries with the Northwind database. This interactive quiz application allows users to solve SQL problems, check their answers, and learn from correct solutions.

## Features

- **Interactive SQL Quiz**: Practice with 50+ SQL questions of varying difficulty
- **Real-time Query Execution**: Connect to Oracle database and execute queries instantly
- **Answer Validation**: Compare your results with correct answers
- **Database Schema Viewer**: Visual reference for table relationships
- **Question Navigation**: Jump to any question or navigate sequentially
- **Hint System**: Get hints when you're stuck
- **Dual Result Display**: See both your results and correct results side by side

## Prerequisites

- Python 3.7+
- Oracle Database
- Required Python packages (install via `pip install -r requirements.txt`):
  - `tkinter` (usually comes with Python)
  - `oracledb`
  - `Pillow`
  - `json`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/BurakKontas/sql-practice.git
cd sql-practice
```

2. Install required packages:
```bash
pip install oracledb Pillow
```

2.1 Install OracleDB on Docker (Optional):
```bash
docker compose up -d
docker compose exec -it oracle-db sqlplus system/testpassword@XEPDB1 @/tmp/Northwind.create.sql
```

Configuration (./db_config.json):
```json
{
    "username": "NORTHWIND",
    "password": "NORTHWIND",
    "dsn": "localhost:1521/XEPDB1"
}
```


3. Set up the Northwind database:
   - Run the `Northwind.create.sql` script in your Oracle database
   - Note your database connection details (username, password, DSN)

4. Configure database connection:
   - Run the application
   - Go to Settings → Database Connection Settings
   - Enter your Oracle database credentials

## Usage

1. **Start the application**:
```bash
python sql_questioner.py
```

2. **Configure Database Connection**:
   - Click Settings → Database Connection Settings
   - Enter your Oracle database credentials:
     - Username: Your Oracle username
     - Password: Your Oracle password
     - DSN: Connection string (e.g., `localhost:1521/XEPDB1`)
   - Test the connection to ensure it works

3. **Solve SQL Questions**:
   - Read the question title at the top
   - Click "Show Hint" if you need help
   - Write your SQL query in the text area
   - Click "Check Answer" to validate your solution
   - View results comparison between your query and the correct answer

4. **Navigate Questions**:
   - Use "Next Question" to move to the next question
   - Or enter a question number (1-50) and click "Go" to jump directly

5. **View Database Schema**:
   - Click "Show Schema" to see the Northwind database structure
   - Use this as a reference while writing queries

## Database Schema

The application uses the classic Northwind database with the following main tables:
- **Customers**: Customer information
- **Orders**: Order records
- **Order Details**: Order line items
- **Products**: Product catalog
- **Categories**: Product categories
- **Suppliers**: Supplier information
- **Employees**: Employee records
- **Shippers**: Shipping company details

## Question Types

The quiz includes various SQL concepts:
- Basic SELECT statements
- JOINs (INNER, LEFT, RIGHT)
- Aggregate functions (SUM, COUNT, AVG, MAX, MIN)
- GROUP BY and HAVING clauses
- Subqueries
- Window functions
- Complex analytical queries

## File Structure

```
sql-practice/
├── sql_questioner.py          # Main application file
├── sql_questions_combined.json # Question database
├── Northwind.create.sql       # Database creation script
├── schema.png                 # Database schema diagram
├── db_config.json            # Database configuration (auto-generated)
├── .gitignore                # Git ignore file
└── README.md                 # This file
```

## Configuration

The application automatically creates a `db_config.json` file to store your database connection settings. This file is excluded from version control for security.

Example configuration:
```json
{
    "username": "your_username",
    "password": "your_password",
    "dsn": "localhost:1521/XEPDB1"
}
```

## Troubleshooting

### Database Connection Issues
- Ensure Oracle database is running
- Verify connection credentials
- Check if the DSN format is correct
- Make sure the Northwind database schema is properly installed

### Missing Schema Image
- Ensure `schema.png` is in the same directory as the application
- The schema viewer will show an error if the image file is missing

### Query Execution Errors
- Check your SQL syntax
- Verify table and column names match the Northwind schema
- Some queries may require Oracle-specific SQL syntax

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with Python and Tkinter for the GUI
- Uses the classic Northwind database for realistic SQL practice
- Oracle database connectivity via oracledb package
