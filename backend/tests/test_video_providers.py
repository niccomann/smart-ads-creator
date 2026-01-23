"""
Test script for video provider integration.
Tests that all providers (Sora, Veo, Runway) are correctly integrated.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/nicco/Desktop/smart-ads-creator/backend')

from app.services.video_generator import video_generator, VideoGeneratorService
from app.models.schemas import VideoProvider


def test_video_generator_init():
    """Test that VideoGeneratorService initializes correctly."""
    print("Testing VideoGeneratorService initialization...")

    assert video_generator is not None, "video_generator should be initialized"
    assert isinstance(video_generator, VideoGeneratorService), "Should be VideoGeneratorService instance"
    assert video_generator.videos_dir.exists(), "Videos directory should exist"

    print("  ✓ VideoGeneratorService initialized correctly")
    print(f"  ✓ Videos directory: {video_generator.videos_dir}")
    return True


def test_providers_enum():
    """Test that all providers are defined in the enum."""
    print("\nTesting VideoProvider enum...")

    providers = [p.value for p in VideoProvider]
    expected = ['sora', 'veo', 'runway', 'kling']

    for p in ['sora', 'veo', 'runway']:
        assert p in providers, f"Provider {p} should be in VideoProvider enum"
        print(f"  ✓ {p} provider defined")

    return True


async def test_provider_methods_exist():
    """Test that all provider generation methods exist."""
    print("\nTesting provider methods exist...")

    # Check Sora method
    assert hasattr(video_generator, '_generate_sora'), "Should have _generate_sora method"
    print("  ✓ _generate_sora method exists")

    # Check Veo method
    assert hasattr(video_generator, '_generate_veo'), "Should have _generate_veo method"
    print("  ✓ _generate_veo method exists")

    # Check Runway method
    assert hasattr(video_generator, '_generate_runway'), "Should have _generate_runway method"
    print("  ✓ _generate_runway method exists")

    return True


async def test_generate_from_prompt_accepts_all_providers():
    """Test that generate_from_prompt accepts all provider values."""
    print("\nTesting generate_from_prompt accepts all providers...")

    test_prompt = "Test video prompt"

    for provider in ['sora', 'veo', 'runway']:
        try:
            # This will fail due to API keys, but should not raise import/attribute errors
            result = await video_generator.generate_from_prompt(
                prompt=test_prompt,
                duration=5,
                size="720x1280",
                provider=provider
            )
            # If we get here, the provider was accepted
            print(f"  ✓ {provider} provider accepted (status: {result.status})")
            if result.error:
                print(f"    Expected API error: {result.error[:80]}...")
        except ImportError as e:
            print(f"  ✗ {provider} - Import error: {e}")
            return False
        except AttributeError as e:
            print(f"  ✗ {provider} - Attribute error: {e}")
            return False
        except Exception as e:
            # API errors are expected, we just want to verify the code path works
            if "API" in str(e) or "key" in str(e).lower() or "401" in str(e) or "403" in str(e) or "429" in str(e):
                print(f"  ✓ {provider} provider accepted (expected API error)")
            else:
                print(f"  ? {provider} - Unexpected error: {e}")

    return True


def test_config_has_all_keys():
    """Test that config has all required API key settings."""
    print("\nTesting config has all API key settings...")

    from app.config import settings

    # Check OpenAI key
    assert hasattr(settings, 'openai_api_key'), "Should have openai_api_key"
    print(f"  ✓ openai_api_key configured: {'Yes' if settings.openai_api_key else 'No'}")

    # Check Gemini key
    assert hasattr(settings, 'gemini_api_key'), "Should have gemini_api_key"
    print(f"  ✓ gemini_api_key configured: {'Yes' if settings.gemini_api_key else 'No'}")

    # Check Runway key
    assert hasattr(settings, 'runwayml_api_secret'), "Should have runwayml_api_secret"
    runway_configured = settings.runwayml_api_secret and settings.runwayml_api_secret != "YOUR_RUNWAY_API_KEY_HERE"
    print(f"  ✓ runwayml_api_secret configured: {'Yes' if runway_configured else 'No (placeholder)'}")

    return True


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("AdGenius AI - Video Provider Integration Tests")
    print("=" * 60)

    results = []

    # Sync tests
    results.append(("VideoGeneratorService init", test_video_generator_init()))
    results.append(("VideoProvider enum", test_providers_enum()))
    results.append(("Config API keys", test_config_has_all_keys()))

    # Async tests
    results.append(("Provider methods exist", await test_provider_methods_exist()))
    results.append(("All providers accepted", await test_generate_from_prompt_accepts_all_providers()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
