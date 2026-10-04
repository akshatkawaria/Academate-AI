import api from '../api';

export const generateSkillRoadmap = async (skillName, studentId = 1) => {
  const res = await api.post('/api/skills/generate', {
    skill_name: skillName,
    student_id: studentId,
  });
  return res.data;
};

export const getStudentProfile = async (studentId = 1) => {
  const res = await api.get(`/api/skills/profile/${studentId}`);
  return res.data;
};

export const updateStudentProfile = async (studentId = 1, profileData) => {
  const res = await api.put(`/api/skills/profile/${studentId}`, profileData);
  return res.data;
};

export const checkSkillExists = async (skillName) => {
  const res = await api.get(`/api/skills/check/${encodeURIComponent(skillName)}`);
  return res.data;
};


