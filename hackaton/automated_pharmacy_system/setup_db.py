import mysql.connector

def setup_database():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456' 
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        with open('database/pharmacy.sql', 'r') as f:
            sql_script = f.read()
        
        # Split by semicolon to execute multiple statements
        statements = sql_script.split(';')
        
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    print(f"Executed: {statement[:50]}...")
                except mysql.connector.Error as err:
                    print(f"Skipping/Error: {err}")
        
        conn.commit()
        print("\nDatabase setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    setup_database()
