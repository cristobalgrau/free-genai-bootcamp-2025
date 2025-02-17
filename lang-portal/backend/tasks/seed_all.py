from tasks.seed_manager import SeedManager

def main():
    # Create seed manager without arguments
    seed_manager = SeedManager()
    
    # Seed basic data
    seed_manager.seed_data("basic_greetings.json", "Basic Greetings")
    seed_manager.seed_basic_activity()
    seed_manager.seed_study_session()

if __name__ == "__main__":
    main()