import json
import re
from typing import List, Dict, Any
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

class LinkedInPostCleaner:
    def __init__(self):
        """
        Initialize the LinkedIn Post Cleaner with Groq API key
        
        Args:
            groq_api_key (str): Your Groq API key
        """
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.discovered_tags = set()  # Set to store all unique tags discovered from posts
        self.max_tags = 15  # Maximum number of unique tags allowed
        self.tag_synonyms = {}  # Dictionary to map similar tags to main tags
    
    def detect_language(self, text: str) -> str:
        """
        Detect if the text is English or Urduish (contains Urdu/Hindi words)
        
        Args:
            text (str): The text to analyze
            
        Returns:
            str: 'English' or 'Urduish'
        """
        # Common Urdu/Hindi words and patterns
        urdu_patterns = [
            r'[\u0600-\u06FF]',  # Arabic/Urdu Unicode range
            r'\b(aur|hai|hain|ke|ki|ko|se|me|mein|bhi|nahi|kya|kaise|kab|kahan|yeh|woh|main|ap|aap|bhai|sahab|ji)\b',
            r'\b(thora|thore|bht|bhut|bohot|krna|karna|krte|karte|hoga|hogi|hoge|wala|wali|vale)\b',
            r'\b(paisa|paise|rupay|rupee|lakh|crore|insha|mashaallah|alhamdulillah)\b'
        ]
        
        text_lower = text.lower()
        for pattern in urdu_patterns:
            if re.search(pattern, text_lower):
                return 'Urduish'
        
        return 'English'
    
    def count_lines(self, text: str) -> int:
        """
        Count the number of lines in the text (number of \n + 1)
        
        Args:
            text (str): The text to count lines for
            
        Returns:
            int: Number of lines
        """
        if not text.strip():
            return 0
        return len(text.split('\n'))
    
    def calculate_engagement(self, post_data: Dict[str, Any]) -> int:
        """
        Calculate total engagement from reactions and comments
        
        Args:
            post_data (Dict): The post data containing reactions and comments
            
        Returns:
            int: Total engagement count
        """
        engagement = 0
        
        # Count reactions
        if 'reactions' in post_data and post_data['reactions']:
            engagement += len(post_data['reactions'])
        
        # Count comments
        if 'comments' in post_data and post_data['comments']:
            engagement += len(post_data['comments'])
        
        return engagement
    
    def normalize_and_merge_tags(self, new_tag: str) -> str:
        """
        Normalize and merge similar tags to prevent duplicates and maintain 15 tag limit
        
        Args:
            new_tag (str): The new tag to normalize
            
        Returns:
            str: The normalized/merged tag
        """
        new_tag = new_tag.strip().title()
        
        # Define tag merging rules for similar concepts
        merge_rules = {
            # Financial related
            "Financial Planning": ["Budgeting", "Budget", "Finance", "Money Management"],
            "Investment": ["Investing", "Trading", "Portfolio", "Wealth"],
            "Cryptocurrency": ["Crypto", "Bitcoin", "Ethereum", "Blockchain"],
            
            # Career related  
            "Career Development": ["Career Growth", "Professional Growth", "Job Search", "Career"],
            "Entrepreneurship": ["Startup", "Business", "Entrepreneur"],
            
            # Tech related
            "Technology": ["Tech", "AI", "Software", "Digital"],
            
            # Marketing related
            "Marketing": ["Branding", "Social Media", "Content Marketing"],
            
            # Personal related
            "Personal Growth": ["Self Development", "Learning", "Motivation"],
            "Leadership": ["Management", "Team Building"],
            
            # Professional related
            "Networking": ["Professional Network", "Connections"],
            "Industry Insights": ["Market Trends", "Analysis"],
            
            # Remove location-based and vague tags
            "General": ["Pakistan", "Karachi", "Lahore", "Islamabad", "Location", "City"]
        }
        
        # Check if the new tag should be merged with an existing main tag
        for main_tag, synonyms in merge_rules.items():
            if new_tag in synonyms or any(syn.lower() in new_tag.lower() for syn in synonyms):
                self.tag_synonyms[new_tag] = main_tag
                return main_tag
            # Also check if new_tag is similar to main_tag
            if main_tag.lower() in new_tag.lower() or new_tag.lower() in main_tag.lower():
                self.tag_synonyms[new_tag] = main_tag
                return main_tag
        
        # If we haven't reached the limit, keep the new tag
        if len(self.discovered_tags) < self.max_tags:
            return new_tag
        else:
            # If we've reached the limit, map to the most similar existing tag
            return self.find_most_similar_existing_tag(new_tag)
    
    def find_most_similar_existing_tag(self, new_tag: str) -> str:
        """
        Find the most similar existing tag when we've reached the 15 tag limit
        
        Args:
            new_tag (str): The new tag to find similarity for
            
        Returns:
            str: The most similar existing tag
        """
        new_tag_lower = new_tag.lower()
        
        # Simple keyword matching with existing tags
        for existing_tag in self.discovered_tags:
            existing_lower = existing_tag.lower()
            # Check for word overlap
            new_words = set(new_tag_lower.split())
            existing_words = set(existing_lower.split())
            if new_words & existing_words:  # If there's any word overlap
                return existing_tag
        
        # If no similarity found, return a generic tag
        generic_tags = ["Business", "Technology", "Career Development", "Personal Growth"]
        for generic in generic_tags:
            if generic in self.discovered_tags:
                return generic
        
        # Fallback to first available tag
        return list(self.discovered_tags)[0] if self.discovered_tags else "General"

    def discover_tags_from_text(self, text: str) -> List[str]:
        """
        Use Groq LLM to discover 1 relevant professional tag from the post text
        
        Args:
            text (str): The post text
            
        Returns:
            List[str]: List containing 1 discovered tag
        """
        try:
            prompt = f"""
            Analyze the following LinkedIn post and extract ONLY 1 most relevant professional topic tag.
            
            Guidelines:
            - Return only 1 tag that represents the MAIN professional topic
            - Use 1-2 words maximum (e.g., "Career Development", "Investment", "Technology")
            - Focus on professional/business themes, NOT locations or personal details
            - Avoid vague terms like "General", "Content", "Post"
            - Avoid location names like "Pakistan", "Karachi", "Lahore"
            - Choose the most specific professional category
            - Make it broad enough to be reusable across similar posts
            
            Examples of good tags: "Investment", "Career Development", "Entrepreneurship", "Technology", "Marketing"
            Examples of bad tags: "Pakistan", "Karachi", "Personal", "General", "Content"
            
            Post text: "{text}"
            
            Return only 1 tag, nothing else.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.1,  # Very low temperature for consistent categorization
                max_tokens=20
            )
            
            raw_tag = response.choices[0].message.content.strip()
            
            # Normalize and merge the tag
            normalized_tag = self.normalize_and_merge_tags(raw_tag)
            
            # Add to discovered tags set
            self.discovered_tags.add(normalized_tag)
            
            return [normalized_tag]
            
        except Exception as e:
            print(f"Error discovering tags with Groq: {e}")
            # Fallback to keyword-based tag extraction
            return self.extract_tags_fallback(text)
    
    def extract_tags_fallback(self, text: str) -> List[str]:
        """
        Fallback method to extract 1 tag using simple keyword analysis
        
        Args:
            text (str): The post text
            
        Returns:
            List[str]: List containing 1 extracted tag
        """
        text_lower = text.lower()
        
        # Define main professional categories with keywords
        main_categories = {
            "Career Development": ["job", "career", "interview", "resume", "hiring", "work", "employment"],
            "Entrepreneurship": ["startup", "business", "entrepreneur", "company", "founder"],
            "Technology": ["tech", "ai", "software", "coding", "digital", "development"],
            "Investment": ["investment", "crypto", "trading", "portfolio", "wealth", "money"],
            "Marketing": ["marketing", "brand", "content", "social", "advertising"],
            "Personal Growth": ["growth", "learning", "motivation", "success", "development"],
            "Leadership": ["leadership", "management", "team", "leader", "mentor"],
            "Networking": ["network", "connection", "linkedin", "professional", "relationship"],
            "Education": ["education", "learning", "skill", "training", "course"],
            "Healthcare": ["health", "medical", "healthcare", "wellness", "fitness"],
            "Finance": ["financial", "budget", "planning", "economy", "banking"],
            "Sales": ["sales", "customer", "client", "revenue", "deal"],
            "Consulting": ["consulting", "advice", "strategy", "solution", "expert"],
            "Innovation": ["innovation", "creative", "idea", "solution", "breakthrough"],
            "Communication": ["communication", "presentation", "speaking", "writing", "message"]
        }
        
        # Find the best matching category
        best_match = "Business"  # Default fallback
        max_score = 0
        
        for category, keywords in main_categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > max_score:
                max_score = score
                best_match = category
        
        # Normalize and add to discovered tags
        normalized_tag = self.normalize_and_merge_tags(best_match)
        self.discovered_tags.add(normalized_tag)
        
        return [normalized_tag]
    
    def clean_text(self, text: str) -> str:
        """
        Clean the post text by removing extra whitespace and normalizing
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace but preserve line breaks
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines]
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def process_single_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single LinkedIn post and convert it to the desired format
        
        Args:
            post_data (Dict): Raw post data from Apify
            
        Returns:
            Dict: Processed post data
        """
        # Extract and clean text
        raw_text = post_data.get('text', '')
        cleaned_text = self.clean_text(raw_text)
        
        # Skip empty posts
        if not cleaned_text:
            return None
        
        # Calculate metrics
        engagement = self.calculate_engagement(post_data)
        line_count = self.count_lines(cleaned_text)
        language = self.detect_language(cleaned_text)
        tags = self.discover_tags_from_text(cleaned_text)  # This now returns only 1 tag
        
        return {
            "text": cleaned_text,
            "engagement": engagement,
            "line_count": line_count,
            "language": language,
            "tags": tags
        }
    
    def process_posts(self, posts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple LinkedIn posts
        
        Args:
            posts_data (List[Dict]): List of raw post data from Apify
            
        Returns:
            List[Dict]: List of processed posts
        """
        processed_posts = []
        
        for i, post_data in enumerate(posts_data):
            try:
                print(f"Processing post {i+1}/{len(posts_data)}...")
                processed_post = self.process_single_post(post_data)
                
                if processed_post:
                    processed_posts.append(processed_post)
                else:
                    print(f"Skipped post {i+1} (empty or invalid)")
                    
            except Exception as e:
                print(f"Error processing post {i+1}: {e}")
                continue
        
        return processed_posts
    
    def save_results(self, processed_posts: List[Dict[str, Any]], output_file: str):
        """
        Save processed posts and discovered tags to a JSON file
        
        Args:
            processed_posts (List[Dict]): Processed posts data
            output_file (str): Output file path
        """
        # Ensure we don't exceed 15 tags
        final_tags = sorted(list(self.discovered_tags))[:self.max_tags]
        
        # Create final output structure
        final_output = {
            "posts": processed_posts,
            "discovered_tags": final_tags,
            "tag_synonyms": self.tag_synonyms,  # Show which tags were merged
            "total_posts": len(processed_posts),
            "total_unique_tags": len(final_tags)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")
        print(f"Discovered {len(final_tags)} unique tags from {len(processed_posts)} posts")
        print(f"Tags: {final_tags}")
        if self.tag_synonyms:
            print(f"Merged tags: {self.tag_synonyms}")


def main():
    """
    Main function to demonstrate usage
    """
    # Set your Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Replace with your actual API key
    
    # Initialize the cleaner
    cleaner = LinkedInPostCleaner(GROQ_API_KEY)
    
    # Load your scraped data
    input_file = "data/linkedin_posts.json"  # Replace with your input file path
    output_file = "data/cleaned_linkedin_posts.json"
    
    try:
        # Load the scraped data
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # If your JSON structure is different, adjust this
        # For example, if your data is wrapped in another structure:
        # posts_data = raw_data.get('posts', raw_data)
        posts_data = raw_data if isinstance(raw_data, list) else [raw_data]
        
        print(f"Loaded {len(posts_data)} posts from {input_file}")
        
        # Process the posts
        processed_posts = cleaner.process_posts(posts_data)
        
        print(f"Successfully processed {len(processed_posts)} posts")
        
        # Save results
        cleaner.save_results(processed_posts, output_file)
        
        # Print sample results
        if processed_posts:
            print("\nSample processed post:")
            print(json.dumps(processed_posts[0], indent=2, ensure_ascii=False))
            
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        print("Please make sure the file exists and the path is correct.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{input_file}'")
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    # Uncomment the function you want to run:
    
    # For processing your actual data file:
     main()
    
    # For testing with the sample data:
    #process_sample_data()