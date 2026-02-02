import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { updateUserProfile } from '../services/apiService';
import { useNavigate } from 'react-router-dom';
import {
    User, Calendar, MapPin, Briefcase, GraduationCap, Globe, Heart,
    Edit2, Save, X, LogOut, Camera, Mail, Shield, Award
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ThemeSwitcher from './ThemeSwitcher';

// --- Sub-components for cleaner code ---

const SectionCard = ({ title, icon: Icon, children, className = "" }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`bg-white/60 backdrop-blur-xl rounded-3xl p-6 shadow-theme border border-white/50 ${className}`}
    >
        <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl">
                <Icon className="w-5 h-5 text-indigo-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-800">{title}</h3>
        </div>
        {children}
    </motion.div>
);

const InfoRow = ({ label, value, icon: Icon }) => (
    <div className="flex items-start gap-4 p-3 rounded-xl hover:bg-white/50 transition-colors group">
        <div className="mt-1 p-1.5 bg-gray-50 rounded-lg group-hover:bg-white transition-colors">
            <Icon className="w-4 h-4 text-gray-400 group-hover:text-indigo-500 transition-colors" />
        </div>
        <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">{label}</p>
            <p className="text-gray-800 font-medium">{value || 'Not set'}</p>
        </div>
    </div>
);

const EditField = ({ label, name, value, onChange, type = "text", options = null, icon: Icon }) => (
    <div className="bg-white/50 p-3 rounded-xl border border-gray-100 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
        <label className="flex items-center gap-2 text-xs font-semibold text-gray-500 mb-1.5">
            <Icon className="w-3 h-3" /> {label}
        </label>
        {options ? (
            <select
                name={name}
                value={value}
                onChange={onChange}
                className="w-full bg-transparent font-medium text-gray-800 focus:outline-none"
            >
                <option value="">Select {label}</option>
                {options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                ))}
            </select>
        ) : (
            <input
                type={type}
                name={name}
                value={value}
                onChange={onChange}
                className="w-full bg-transparent font-medium text-gray-800 placeholder-gray-400 focus:outline-none"
                placeholder={`Enter ${label}`}
            />
        )}
    </div>
);

export default function UserProfile() {
    const { user, setUser, logout } = useStore();
    const navigate = useNavigate();
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(false);

    // Local state for the form - initialized from user store
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        date_of_birth: '',
        gender: '',
        city: '',
        address: '',
        occupation: '',
        education: '',
        industry_domain: '',
        hobbies: ''
    });

    useEffect(() => {
        if (user) {
            setFormData({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                email: user.email || '',
                date_of_birth: user.date_of_birth || '',
                gender: user.gender || '',
                city: user.city || '',
                address: user.address || '',
                occupation: user.occupation || '',
                education: user.education || '',
                industry_domain: user.industry_domain || '',
                hobbies: user.hobbies || ''
            });
        }
    }, [user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = async () => {
        setLoading(true);
        try {
            // Call the API via service wrapper
            const response = await updateUserProfile(formData);

            // Update local store with new user data
            const updatedUser = { ...user, ...formData, ...response?.user };
            setUser(updatedUser);
            localStorage.setItem('user', JSON.stringify(updatedUser));

            setIsEditing(false);
        } catch (error) {
            console.error("Failed to update profile", error);
            // Ideally show a toast here
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    // Safe fallback for user data
    if (!user) return null;

    const hobbyList = formData.hobbies
        ? formData.hobbies.split(',').map(h => h.trim()).filter(Boolean)
        : [];

    return (
        <div className="min-h-screen bg-gradient-theme pb-20 pt-6 px-4 sm:px-6">
            <div className="max-w-6xl mx-auto space-y-6">

                {/* --- Hero Section --- */}
                <div className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-r from-indigo-600 to-purple-700 shadow-2xl p-8 sm:p-12 text-white">
                    {/* Decorative background circles */}
                    <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl" />

                    <div className="relative z-10 flex flex-col sm:flex-row items-center sm:items-end gap-6 sm:gap-8 justify-between">
                        <div className="flex flex-col sm:flex-row items-center gap-6">
                            <div className="relative group">
                                <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-white/20 backdrop-blur-md p-1 border-2 border-white/30 shadow-xl overflow-hidden">
                                    <div className="w-full h-full rounded-full bg-gradient-to-br from-indigo-100 to-white flex items-center justify-center text-indigo-600 font-bold text-3xl sm:text-4xl">
                                        {user.first_name?.[0]}{user.last_name?.[0]}
                                    </div>
                                </div>
                                <button className="absolute bottom-0 right-0 p-2 bg-white text-indigo-600 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity transform scale-90 hover:scale-100">
                                    <Camera className="w-4 h-4" />
                                </button>
                            </div>

                            <div className="text-center sm:text-left">
                                <p className="text-indigo-200 font-medium mb-1 tracking-wide uppercase text-xs sm:text-sm">Identity Passport</p>
                                <h1 className="text-3xl sm:text-4xl font-bold mb-2">{user.first_name} {user.last_name}</h1>
                                <div className="flex flex-wrap items-center justify-center sm:justify-start gap-4 text-sm text-indigo-100/90 font-medium">
                                    <span className="flex items-center gap-1.5 bg-white/10 px-3 py-1 rounded-full"><Award className="w-4 h-4" /> {user.occupation || 'Explorer'}</span>
                                    <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4" /> {user.city || 'Digital Nomad'}</span>
                                </div>
                            </div>
                        </div>

                        {/* Main Action Buttons */}
                        <div className="flex items-center gap-3 w-full sm:w-auto mt-4 sm:mt-0">
                            {!isEditing ? (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white px-5 py-2.5 rounded-full transition-all font-medium"
                                >
                                    <Edit2 className="w-4 h-4" /> Edit Profile
                                </button>
                            ) : (
                                <>
                                    <button
                                        onClick={() => setIsEditing(false)}
                                        className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-red-500/20 hover:bg-red-500/30 text-white px-5 py-2.5 rounded-full transition-all font-medium"
                                    >
                                        <X className="w-4 h-4" /> Cancel
                                    </button>
                                    <button
                                        onClick={handleSave}
                                        disabled={loading}
                                        className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-white text-indigo-600 px-6 py-2.5 rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all font-bold disabled:opacity-70 disabled:hover:scale-100"
                                    >
                                        {loading ? 'Saving...' : <><Save className="w-4 h-4" /> Save Changes</>}
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                {/* --- Content Grid --- */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Column 1: Personal & Account */}
                    <div className="space-y-6">
                        {/* Personal Details Card */}
                        <SectionCard title="Personal Details" icon={User}>
                            <div className="space-y-2">
                                {isEditing ? (
                                    <div className="space-y-4 animate-fade-in">
                                        <div className="grid grid-cols-2 gap-3">
                                            <EditField label="First Name" name="first_name" value={formData.first_name} onChange={handleChange} icon={User} />
                                            <EditField label="Last Name" name="last_name" value={formData.last_name} onChange={handleChange} icon={User} />
                                        </div>
                                        <EditField label="Date of Birth" name="date_of_birth" type="date" value={formData.date_of_birth} onChange={handleChange} icon={Calendar} />
                                        <EditField label="Gender" name="gender" options={["Male", "Female", "Non-binary", "Prefer not to say"]} value={formData.gender} onChange={handleChange} icon={User} />
                                        <EditField label="City" name="city" value={formData.city} onChange={handleChange} icon={MapPin} />
                                        <EditField label="Address" name="address" value={formData.address} onChange={handleChange} icon={JobIcon} />
                                    </div>
                                ) : (
                                    <div className="space-y-1">
                                        <InfoRow label="Full Name" value={`${formData.first_name} ${formData.last_name}`} icon={User} />
                                        <InfoRow label="Email" value={formData.email} icon={Mail} />
                                        <InfoRow label="Date of Birth" value={formData.date_of_birth} icon={Calendar} />
                                        <InfoRow label="Gender" value={formData.gender} icon={User} />
                                        <InfoRow label="Location" value={`${formData.address ? formData.address + ', ' : ''}${formData.city}`} icon={MapPin} />
                                    </div>
                                )}
                            </div>
                        </SectionCard>

                        {/* Preferences Card */}
                        <SectionCard title="Preferences" icon={Shield}>
                            <div className="flex flex-col gap-4">
                                <div className="flex items-center justify-between p-3 bg-gray-50/50 rounded-2xl border border-gray-100">
                                    <span className="text-gray-600 font-medium text-sm ml-2">App Theme</span>
                                    <ThemeSwitcher />
                                </div>

                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center justify-center gap-2 p-3 text-red-600 font-medium hover:bg-red-50 rounded-xl transition-colors text-sm"
                                >
                                    <LogOut className="w-4 h-4" /> Sign Out from Device
                                </button>
                            </div>
                        </SectionCard>
                    </div>

                    {/* Column 2: Professional Journey */}
                    <div className="lg:col-span-2 space-y-6">
                        <SectionCard title="Professional Journey" icon={Briefcase}>
                            {isEditing ? (
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fade-in">
                                    <EditField label="Occupation" name="occupation" value={formData.occupation} onChange={handleChange} icon={Briefcase} />
                                    <EditField label="Industry Domain" name="industry_domain" value={formData.industry_domain} onChange={handleChange} icon={Globe} />
                                    <div className="sm:col-span-2">
                                        <EditField label="Education" name="education" value={formData.education} onChange={handleChange} icon={GraduationCap} />
                                    </div>
                                </div>
                            ) : (
                                <div className="relative pl-6 border-l-2 border-indigo-100 space-y-8 py-2">
                                    <div className="relative">
                                        <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 border-white bg-indigo-500 shadow-md"></div>
                                        <h4 className="text-lg font-bold text-gray-900">{formData.occupation || 'Define your role'}</h4>
                                        <p className="text-indigo-600 font-medium text-sm mb-1">{formData.industry_domain || 'Your Industry'}</p>
                                        <p className="text-gray-500 text-sm leading-relaxed">Currently navigating the professional landscape in this domain.</p>
                                    </div>

                                    <div className="relative">
                                        <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 border-white bg-purple-400 shadow-md"></div>
                                        <h4 className="text-lg font-bold text-gray-900">{formData.education || 'Add your education'}</h4>
                                        <p className="text-gray-500 text-sm">Academic Background</p>
                                    </div>
                                </div>
                            )}
                        </SectionCard>

                        <SectionCard title="Interests & Passions" icon={Heart}>
                            {isEditing ? (
                                <div className="space-y-3 animate-fade-in">
                                    <p className="text-xs text-gray-500">Add your hobbies separated by commas</p>
                                    <textarea
                                        name="hobbies"
                                        value={formData.hobbies}
                                        onChange={handleChange}
                                        rows={3}
                                        className="w-full bg-white/50 p-4 rounded-xl border border-gray-100 focus:ring-2 focus:ring-indigo-100 focus:outline-none resize-none font-medium text-gray-700"
                                        placeholder="e.g. Hiking, Photography, Jazz Music..."
                                    />
                                </div>
                            ) : (
                                <div className="flex flex-wrap gap-2">
                                    {hobbyList.length > 0 ? hobbyList.map((hobby, i) => (
                                        <span key={i} className="px-4 py-2 bg-white rounded-full text-sm font-medium text-gray-700 shadow-sm border border-gray-100 hover:scale-105 hover:bg-indigo-50 hover:text-indigo-600 transition-all cursor-default select-none">
                                            {hobby}
                                        </span>
                                    )) : (
                                        <p className="text-gray-400 italic text-sm">No hobbies added yet. Use the edit button to add some!</p>
                                    )}
                                </div>
                            )}
                        </SectionCard>
                    </div>

                </div>
            </div>
        </div>
    );
}

// Helper icon
const JobIcon = ({ className }) => <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>;
