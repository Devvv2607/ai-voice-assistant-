#!/usr/bin/env python3
"""
Setup script for Jarvis AI Assistant.
Handles installation, configuration, and initial setup.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class JarvisSetup:
    """Setup and configuration manager for Jarvis AI Assistant."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / 'config'
        self.requirements_file = self.project_root / 'requirements.txt'
        
    def run_full_setup(self):
        """Run complete setup process."""
        logger.info("🚀 Starting Jarvis AI Assistant Setup")
        logger.info("="*50)
        
        try:
            self.check_python_version()
            self.install_dependencies()
            self.setup_nltk_data()
            self.setup_configuration_files()
            self.setup_directories()
            self.verify_installation()
            self.display_next_steps()
            
            logger.info("✅ Setup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            sys.exit(1)
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        logger.info("🐍 Checking Python version...")
        
        python_version = sys.version_info
        min_version = (3, 8)
        
        if python_version < min_version:
            raise RuntimeError(
                f"Python {min_version[0]}.{min_version[1]}+ is required. "
                f"You have Python {python_version.major}.{python_version.minor}"
            )
        
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    def install_dependencies(self):
        """Install required Python packages."""
        logger.info("📦 Installing dependencies...")
        
        if not self.requirements_file.exists():
            raise FileNotFoundError("requirements.txt not found")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            logger.info("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e.stderr}")
            raise
    
    def setup_nltk_data(self):
        """Download required NLTK data."""
        logger.info("🔤 Setting up NLTK data...")
        
        try:
            import nltk
            
            # Download required NLTK data
            nltk_downloads = ['punkt', 'stopwords', 'averaged_perceptron_tagger']
            
            for dataset in nltk_downloads:
                try:
                    nltk.data.find(f'tokenizers/{dataset}')
                except LookupError:
                    try:
                        nltk.data.find(f'corpora/{dataset}')
                    except LookupError:
                        logger.info(f"Downloading {dataset}...")
                        nltk.download(dataset, quiet=True)
            
            logger.info("✅ NLTK data setup complete")
            
        except ImportError:
            logger.warning("⚠️  NLTK not installed, skipping NLTK data setup")
        except Exception as e:
            logger.warning(f"⚠️  NLTK data setup failed: {e}")
    
    def setup_configuration_files(self):
        """Setup configuration files from examples."""
        logger.info("⚙️  Setting up configuration files...")
        
        config_files = [
            ('.env.example', '.env'),
            ('credentials.json.example', 'credentials.json')
        ]
        
        for example_file, target_file in config_files:
            example_path = self.config_dir / example_file
            target_path = self.project_root / target_file
            
            if not target_path.exists() and example_path.exists():
                shutil.copy2(example_path, target_path)
                logger.info(f"Created {target_file} from example")
            elif target_path.exists():
                logger.info(f"{target_file} already exists, skipping")
            else:
                logger.warning(f"⚠️  {example_file} not found, skipping {target_file}")
    
    def setup_directories(self):
        """Create necessary directories."""
        logger.info("📁 Creating directories...")
        
        directories = [
            'logs',
            'data',
            'temp'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def verify_installation(self):
        """Verify that installation was successful."""
        logger.info("🔍 Verifying installation...")
        
        # Check if main module can be imported
        try:
            sys.path.insert(0, str(self.project_root))
            import jarvis
            logger.info("✅ Jarvis module can be imported")
        except ImportError as e:
            logger.error(f"❌ Failed to import Jarvis module: {e}")
            raise
        
        # Check critical dependencies
        critical_deps = [
            'speech_recognition',
            'pyttsx3',
            'requests',
            'langchain',
            'nltk'
        ]
        
        missing_deps = []
        for dep in critical_deps:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            raise ImportError(f"Missing critical dependencies: {', '.join(missing_deps)}")
        
        logger.info("✅ All critical dependencies are available")
    
    def display_next_steps(self):
        """Display next steps for user."""
        logger.info("\n" + "="*50)
        logger.info("🎉 SETUP COMPLETE!")
        logger.info("="*50)
        logger.info("\n📋 NEXT STEPS:")
        logger.info("\n1. 🔑 Configure API Keys:")
        logger.info("   - Edit .env file with your API keys")
        logger.info("   - See docs/API_KEYS.md for detailed instructions")
        
        logger.info("\n2. 📅 Setup Google Calendar (Optional):")
        logger.info("   - Follow instructions in docs/SETUP.md")
        logger.info("   - Place credentials.json in project root")
        
        logger.info("\n3. 🎤 Test Audio Setup:")
        logger.info("   - Ensure microphone and speakers are working")
        logger.info("   - Test with: python -c \"import speech_recognition; print('Audio OK')\"")
        
        logger.info("\n4. 🚀 Run Jarvis:")
        logger.info("   - python main.py")
        
        logger.info("\n5. 📖 Read Documentation:")
        logger.info("   - docs/README.md - Overview and features")
        logger.info("   - docs/SETUP.md - Detailed setup guide")
        logger.info("   - docs/API_KEYS.md - API configuration guide")
        
        logger.info("\n⚠️  IMPORTANT NOTES:")
        logger.info("- Update .env with your actual API keys before running")
        logger.info("- Some features require internet connection")
        logger.info("- First run may take longer due to model downloads")
        
        logger.info("\n🆘 Need Help?")
        logger.info("- Check logs/jarvis.log for detailed error messages")
        logger.info("- Review troubleshooting section in docs/SETUP.md")


def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Jarvis AI Assistant Setup')
    parser.add_argument('--deps-only', action='store_true', 
                       help='Only install dependencies')
    parser.add_argument('--config-only', action='store_true',
                       help='Only setup configuration files')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify installation')
    
    args = parser.parse_args()
    
    setup = JarvisSetup()
    
    try:
        if args.deps_only:
            setup.check_python_version()
            setup.install_dependencies()
            setup.setup_nltk_data()
        elif args.config_only:
            setup.setup_configuration_files()
            setup.setup_directories()
        elif args.verify_only:
            setup.verify_installation()
        else:
            setup.run_full_setup()
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()