module.exports = {
  trigger: "pre-commit",
  action: async () => {
    await generateDocs();
    await updateChangelog();
    // Generate API documentation from code
    await generateApiDocs();

    // Update component documentation
    await updateComponentDocs();

    // Sync README with current features
    await syncReadmeWithCode();

    // Update changelog
    await updateChangelog();
  },
};
